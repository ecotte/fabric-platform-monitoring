# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "jupyter",
# META     "jupyter_kernel_name": "python3.11"
# META   }
# META }

# CELL ********************

%pip install fabric-deployment-tool --quiet

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# MARKDOWN ********************

# ## Vairables to Replace
# 
# - Add the list of environments you want to update in a structure approach in environments. It should be an array of object with the following format {"workspace_id": "<guid>", "environment_id": "<guid>"}.

# CELL ********************

environments = [
    {"workspace_id": "", "environment_id": ""},
]

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# MARKDOWN ********************

# ## ****Deployment

# CELL ********************

fabDeploymentTool.fab_update_environments_spark_monitor(environments, workspace_name, "SparkMonitoring","IngestionEndpoint")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }
