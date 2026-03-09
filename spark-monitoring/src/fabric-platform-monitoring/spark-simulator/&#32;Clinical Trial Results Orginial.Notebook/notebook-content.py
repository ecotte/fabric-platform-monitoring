# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "environment": {
# META       "environmentId": "214695a4-2304-89ee-4d06-ed439a7fda4e",
# META       "workspaceId": "00000000-0000-0000-0000-000000000000"
# META     }
# META   }
# META }

# MARKDOWN ********************

# ─────────────────────────────────────────────────────────────
#  ## DEMO: Clinical Trial Results Pipeline  ── BAD PRACTICES
#  #### Bad practices packed in:
#    1. No caching  → same DF recomputed 4 times
#    2. Python UDFs → serialization overhead on every row
#    3. Excessive repartitioning → 4 unnecessary shuffles
#    4. Collect to driver → 5M rows pulled to driver memory
#    5. groupByKey on RDD → full shuffle with no local combine
#    6. SELECT * on wide table → reads all 40 cols, uses 3
#    
# ─────────────────────────────────────────────────────────────

# CELL ********************

from pyspark.sql import functions as F
from pyspark.sql.types import StringType, DoubleType
from datetime import datetime
import time

spark.sparkContext.setJobGroup("VASA_DEMO_BAD", "Clinical Trial Pipeline — BAD PRACTICES")

_start = time.time()
NUM_ROWS = 50_000_000
print(f"{'='*60}")
print(f"  Clinical Trial Pipeline  [BAD PRACTICES]")
print(f"  rows = {NUM_ROWS:,}")
print(f"{'='*60}\n")

# ── Generate wide base table (40 columns) ─────────────────────
print("Step 1: Generating wide base table (40 columns)...")
df = spark.range(NUM_ROWS).withColumn("patient_id",   (F.rand(1) * 100_000).cast("int")) \
                           .withColumn("trial_id",    (F.rand(2) * 500).cast("int")) \
                           .withColumn("site_id",     (F.rand(3) * 50).cast("int")) \
                           .withColumn("dose_mg",     (F.rand(4) * 200 + 10).cast("double")) \
                           .withColumn("age",         (F.rand(5) * 60 + 18).cast("int")) \
                           .withColumn("weight_kg",   (F.rand(6) * 60 + 50).cast("double")) \
                           .withColumn("response",    (F.rand(7) * 100).cast("double")) \
                           .withColumn("adverse",     (F.rand(8) < 0.15).cast("int"))
# Pad to 40 columns (simulates real wide schema)
for i in range(32):
    df = df.withColumn(f"extra_col_{i}", F.rand() * 1000)

# ── BAD 1: SELECT * — reads all 40 cols, only needs 6 ─────────
print("Step 2: [BAD] SELECT * on 40-column table...")
all_cols = df.select("*")

# ── BAD 2: Python UDFs for simple bucketing ───────────────────
print("Step 3: [BAD] Applying Python UDFs (serialization overhead)...")

@F.udf(returnType=StringType())
def age_group_udf(age):
    if age < 30:   return "Young"
    elif age < 50: return "Middle"
    else:          return "Senior"

@F.udf(returnType=StringType())
def dose_category_udf(dose):
    if dose < 50:   return "Low"
    elif dose < 150: return "Medium"
    else:            return "High"

@F.udf(returnType=DoubleType())
def bmi_proxy_udf(weight, age):
    return float(weight / (age * 0.01 + 1.5))

enriched = all_cols.withColumn("age_group",    age_group_udf(F.col("age"))) \
                   .withColumn("dose_cat",     dose_category_udf(F.col("dose_mg"))) \
                   .withColumn("bmi_proxy",    bmi_proxy_udf(F.col("weight_kg"), F.col("age")))

# ── BAD 3: No caching — enriched recomputed 4× ───────────────
print("Step 4: [BAD] 4 actions on un-cached DF (full recompute each time)...")
count1   = enriched.count()
print(f"  Action 1 (count):         {count1:,}")

avg_resp = enriched.agg(F.avg("response")).collect()[0][0]
print(f"  Action 2 (avg response):  {avg_resp:.2f}")

adverse  = enriched.filter(F.col("adverse") == 1).count()
print(f"  Action 3 (adverse count): {adverse:,}")

max_dose = enriched.agg(F.max("dose_mg")).collect()[0][0]
print(f"  Action 4 (max dose):      {max_dose:.1f}")

# ── BAD 4: Excessive repartitioning before aggregation ────────
print("Step 5: [BAD] Repartitioning 4 times unnecessarily...")
enriched = enriched.repartition(200)
enriched = enriched.repartition(50)
enriched = enriched.repartition(400)
enriched = enriched.repartition(20)

# ── BAD 5: groupByKey on RDD — shuffles ALL values ────────────
print("Step 6: [BAD] groupByKey on RDD (no local combine)...")
rdd = enriched.select("trial_id", "response").rdd \
              .map(lambda r: (r["trial_id"], r["response"]))
trial_totals = rdd.groupByKey() \
                  .mapValues(lambda vals: sum(vals) / len(list(vals))) \
                  .count()
print(f"  Trial groups processed: {trial_totals:,}")

# ── BAD 6: Collect 5M rows to driver ─────────────────────────
print("Step 7: [BAD] Collecting full enriched dataset to driver...")
data = enriched.select("patient_id", "age_group", "dose_cat", "response").collect()
print(f"  Collected {len(data):,} rows to driver memory")

_duration = time.time() - _start
spark.sparkContext.setJobGroup("", "")
print(f"\n{'='*60}")
print(f"  [BAD]  Duration: {_duration:.1f}s")
print(f"{'='*60}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
