# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "environment": {}
# META   }
# META }

# CELL ********************

import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pip", "install", 
     "https://raw.githubusercontent.com/anumicrosoftlab/fabric-spark-monitoring/main/Recommender/spark_monitoring_analyzer-0.2.0-py3-none-any.whl"],
    capture_output=True, text=True
)
print(result.stdout)
print(result.stderr)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from spark_monitoring_analyzer import run

run(kusto_uri=kustoUri, database=database)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
