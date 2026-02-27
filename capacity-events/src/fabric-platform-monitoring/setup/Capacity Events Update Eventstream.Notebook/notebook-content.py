# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "jupyter",
# META     "jupyter_kernel_name": "python3.11"
# META   },
# META   "dependencies": {}
# META }

# MARKDOWN ********************

# # ✅ Prerequisites for Capacity Events
# 
# This document outlines the required setup and behavior of the **Capacity Events** solution, which keeps capacity-related events up to date in a Fabric **Eventstream**.
# 
# ---
# 
# ## 🧩 1. Capacity Events Solution Overview
# 
# The Capacity Events solution is driven by a **Fabric notebook** that synchronizes capacity information into an **Eventstream**.
# 
# When the notebook runs:
# - It discovers all **Fabric capacities** where the executing user is an **Administrator**
# - It updates the Eventstream with the current list of those capacities
# - The Eventstream is kept aligned with the administrator’s current access scope
# 
# This ensures capacity events are always emitted for the correct set of capacities.
# 
# ---
# 
# ## 👤 2. Administrator Permissions Requirement
# 
# The behavior of the Capacity Events solution is directly tied to the permissions of the **user who runs the notebook**.
# 
# **Important considerations:**
# - Only capacities where the user is an **Administrator** are included
# - Capacities where the user has no admin access are ignored
# - No manual capacity list is required when running the notebook interactively
# 
# Access control is enforced implicitly through Fabric permissions.
# 
# ---
# 
# ## 📓 3. Running the Notebook
# 
# Running the notebook will:
# - Query all capacities the executing user administers
# - Update the Eventstream configuration accordingly
# - Add new capacities or remove capacities based on the user’s current admin access
# 
# This makes the notebook the **single source of truth** for capacity discovery.
# 
# ---
# 
# ## ▶️ 4. Scheduling Capacity Events with a Pipeline
# 
# If you want to automate the process, you can schedule it using a **Fabric pipeline**.
# 
# To do this:
# - Enable the **pipeline schedule**
# - Ensure the pipeline runs using a **Capacity Administrator identity**
# - The scheduled execution will automatically:
#   - Add any new capacities the administrator has access to
#   - Remove capacities the administrator no longer administers
# 
# No additional configuration is needed to manage capacity membership over time.
# 
# ---
# 
# ## 🧠 Why This Setup Matters
# 
# This approach ensures:
# - ✅ Automatic discovery of administered capacities


# CELL ********************

%pip install fabric-deployment-tool --quiet

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

from sempy import fabric
import fabric_deployment_tool

workspace_id = fabric.get_notebook_workspace_id()
workspace_name = fabric.list_workspaces(filter=f"id eq '{workspace_id}'").at[0,'Name']

fabDeploymentTool = fabric_deployment_tool.FabDeploymentTool()

fabDeploymentTool.update_capcity_events_eventstream(workspace_name)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }
