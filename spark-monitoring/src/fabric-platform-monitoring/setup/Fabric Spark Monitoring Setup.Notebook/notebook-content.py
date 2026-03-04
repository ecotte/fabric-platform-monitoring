# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "jupyter",
# META     "jupyter_kernel_name": "python3.11"
# META   }
# META }

# MARKDOWN ********************

# ## Vairables to Replace
# 
# - Add the list of environments you want to update in a structure approach in environments. It should be an array of object with the following format {"workspace_id": "<guid>", "environment_id": "<guid>"}.

# CELL ********************

%pip install fabric-deployment-tool --quiet
%pip install semantic-link-labs --quiet

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

environments = [
    # {"workspace_id": "", "environment_id": ""},
]

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

import sempy_labs.environment as labs_env
import sempy.fabric as fabric
import fabric_deployment_tool

fabDeploymentTool = fabric_deployment_tool.FabDeploymentTool()

env = labs_env.list_environments()

emulator_env = {"workspace_id":fabric.get_workspace_id(),"environment_id":env[env["Environment Name"] == "vasa-spark-simulator"]["Environment Id"].values[0]}

environments.append(emulator_env)

fabDeploymentTool.fab_update_environments_spark_monitor(environments, fabric.list_workspaces(filter=f"id eq '{fabric.get_workspace_id()}'")["Name"].values[0], "SparkMonitoringStream","IngestionEndpoint")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }
