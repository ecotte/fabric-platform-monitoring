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

import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pip", "install", 
     "https://raw.githubusercontent.com/anumicrosoftlab/fabric-spark-monitoring/main/SparkSimulator/vasa_spark_simulator-0.1.0-py3-none-any.whl"],
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

from vasa_spark_simulator import pipeline_entry
import json, sys

JOB_NUMBER       = actual_job
NUM_ROWS         = 1_000_000
DURATION_MINUTES = 2

print(f"{'='*60}")
print(f"  Running job #{JOB_NUMBER}  |  rows={NUM_ROWS:,}  |  duration={DURATION_MINUTES}m")
print(f"{'='*60}")

result = pipeline_entry(JOB_NUMBER, num_rows=NUM_ROWS, duration_minutes=DURATION_MINUTES)

print(f"\n{'='*60}")
print(f"  Status   : {result['status']}")
print(f"  Job      : {result.get('job_name', 'n/a')}  (#{result.get('job_number', 'n/a')})")
print(f"  Duration : {result.get('duration', 0):.2f}s")
if result['status'] == 'success':
    print(f"  Message  : {result.get('message', '')}")
else:
    print(f"  Error    : {result.get('error', 'unknown')}")
print(f"{'='*60}")

print(f"\nFull result:\n{json.dumps(result, indent=2, default=str)}")

if result['status'] == 'failed':
    sys.exit(1)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
