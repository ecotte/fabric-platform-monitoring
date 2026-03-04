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

# CELL ********************

# ── 8 Fabric best-practice configs tracked by Spark Monitoring Analyzer ───────
spark.conf.set("spark.databricks.delta.autoCompact.enabled",                "true")
spark.conf.set("spark.microsoft.delta.targetFileSize.adaptive.enabled",     "true")
spark.conf.set("spark.microsoft.delta.optimize.fast.enabled",               "true")
spark.conf.set("spark.microsoft.delta.optimize.fileLevelTarget.enabled",    "true")
spark.conf.set("spark.microsoft.delta.stats.collect.extended",              "true")
spark.conf.set("spark.microsoft.delta.snapshot.driverMode.enabled",         "true")
spark.conf.set("spark.sql.parquet.vorder.default",                          "false")  # reduces Power BI overhead
spark.conf.set("spark.microsoft.delta.optimizeWrite.enabled",               "false")  # avoids bin-pack overhead
spark.conf.set("spark.native.enabled",                                      "true")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# ─────────────────────────────────────────────────────────────
#  DEMO: Clinical Trial Results Pipeline  ── OPTIMIZED
#  Fixes applied:
#    1. Cache once  → zero recomputation
#    2. F.when()    → no Python serialization
#    3. Select only needed columns upfront
#    4. Single repartition on join key
#    5. DataFrame groupBy().agg() → local combine + shuffle
#    6. count() only — no driver collect
# ─────────────────────────────────────────────────────────────
from pyspark.sql import functions as F
import time

spark.sparkContext.setJobGroup("VASA_DEMO_OPT", "Clinical Trial Pipeline — OPTIMIZED")

_start = time.time()
NUM_ROWS = 50_000_000
print(f"{'='*60}")
print(f"  Clinical Trial Pipeline  [OPTIMIZED]")
print(f"  rows = {NUM_ROWS:,}")
print(f"{'='*60}\n")

# ── FIX 3: Select only the 6 columns we actually need ─────────
print("Step 1: Generating table with column pruning (6 cols only)...")
df = spark.range(NUM_ROWS).select(
    (F.rand(1) * 100_000).cast("int").alias("patient_id"),
    (F.rand(2) * 500).cast("int").alias("trial_id"),
    (F.rand(4) * 200 + 10).cast("double").alias("dose_mg"),
    (F.rand(5) * 60 + 18).cast("int").alias("age"),
    (F.rand(6) * 60 + 50).cast("double").alias("weight_kg"),
    (F.rand(7) * 100).cast("double").alias("response"),
    (F.rand(8) < 0.15).cast("int").alias("adverse"),
)

# ── FIX 2: Built-in F.when() instead of UDFs ─────────────────
print("Step 2: Enriching with built-in expressions (no UDFs)...")
enriched = df.withColumn(
    "age_group",
    F.when(F.col("age") < 30, F.lit("Young"))
     .when(F.col("age") < 50, F.lit("Middle"))
     .otherwise(F.lit("Senior"))
).withColumn(
    "dose_cat",
    F.when(F.col("dose_mg") < 50,  F.lit("Low"))
     .when(F.col("dose_mg") < 150, F.lit("Medium"))
     .otherwise(F.lit("High"))
).withColumn(
    "bmi_proxy",
    F.col("weight_kg") / (F.col("age") * 0.01 + 1.5)
)

# ── FIX 1: Cache once, reuse for all 4 actions ───────────────
print("Step 3: Caching (once) before multiple actions...")
enriched.cache()
_ = enriched.count()  # materialise cache

print("Step 4: 4 actions on cached DF (no recomputation)...")
count1   = enriched.count()
print(f"  Action 1 (count):         {count1:,}")

avg_resp = enriched.agg(F.avg("response")).collect()[0][0]
print(f"  Action 2 (avg response):  {avg_resp:.2f}")

adverse  = enriched.filter(F.col("adverse") == 1).count()
print(f"  Action 3 (adverse count): {adverse:,}")

max_dose = enriched.agg(F.max("dose_mg")).collect()[0][0]
print(f"  Action 4 (max dose):      {max_dose:.1f}")

# ── FIX 4 & 5: Single repartition + DataFrame groupBy().agg() ─
print("Step 5: Single repartition on join key + DataFrame agg (local combine)...")
trial_summary = enriched.repartition("trial_id") \
    .groupBy("trial_id") \
    .agg(F.avg("response").alias("avg_response"),
         F.count("*").alias("patient_count")) \
    .count()
print(f"  Trial groups processed: {trial_summary:,}")

# ── FIX 6: count() only — nothing pulled to driver ───────────
print("Step 6: count() only — no collect() to driver...")
total = enriched.select("patient_id", "age_group", "dose_cat", "response").count()
print(f"  Processed {total:,} rows (stayed on executors)")

enriched.unpersist()

_duration = time.time() - _start
spark.sparkContext.setJobGroup("", "")
print(f"\n{'='*60}")
print(f"  [OPT]  Duration: {_duration:.1f}s")
print(f"{'='*60}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
