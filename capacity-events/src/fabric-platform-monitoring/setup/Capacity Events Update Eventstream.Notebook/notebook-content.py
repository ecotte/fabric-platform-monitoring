# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "jupyter",
# META     "jupyter_kernel_name": "python3.12"
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

%pip install ms-fabric-cli==1.6.1 --quiet

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

from sempy import fabric
import subprocess
import json
import shutil
import uuid

workspace_id = fabric.get_notebook_workspace_id()
workspace_name = fabric.list_workspaces(filter=f"id eq '{workspace_id}'").at[0,'Name']

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

def run_fab_command(
    command,
    capture_output: bool = False,
    silently_continue: bool = False,
    raw_output: bool = False,
):
    result = subprocess.run(
        ["fab", "-c", command], capture_output=capture_output, text=True
    )
    if not (silently_continue) and (result.returncode > 0 or result.stderr):
        raise Exception(
            f"Error running fab command. exit_code: '{result.returncode}'; stderr: '{result}'"
        )
    if capture_output and not raw_output:
        output = result.stdout.strip()
        return output
    elif capture_output and raw_output:
        return result

def update_capcity_events_eventstream(workspace, item_name="CapacityEvents"):
    tmp_path = "./builtin/tmp/export/"

    shutil.rmtree(tmp_path, ignore_errors=True)

    os.makedirs(os.path.dirname(tmp_path), exist_ok=True)

    run_fab_command(
        f"export  /{workspace}.Workspace/{item_name}.Eventstream -o {tmp_path} -f ",
        silently_continue=True,
    )

    property_file = f"{tmp_path}{item_name}.Eventstream/eventstream.json"

    new_sources = []
    new_input_nodes = []

    dfCapacities = fabric.list_capacities()
    dfCapacities = dfCapacities.query("Sku != 'PP3'")

    with open(property_file, "r", encoding="utf-8") as file:
        content = json.load(file)
        sources = content.get("sources", [])
        for index, row in dfCapacities.iterrows():
            capacity_id = row["Id"]
            name = row["Display Name"]
            sku = row["Sku"]
            name = f"{name.replace(' ','')}-{sku}"
            name = name.replace("_", "")
            ## Overview Events
            filtered_data = list(
                filter(
                    lambda table: 
                        table.get("properties", {}).get("capacityId") == capacity_id 
                        and table.get("type") == "FabricCapacityOverviewEvents",
                    sources,
                )
            )
            if len(filtered_data) > 0:
                new_source = filtered_data.pop()
                new_input_node = {"name": new_source.get("name")}
            else:
                new_source = {
                    "id": str(uuid.uuid4()),
                    "name": name,
                    "type": "FabricCapacityOverviewEvents",
                    "properties": {
                        "eventScope": "Capacity",
                        "capacityId": capacity_id,
                        "includedEventTypes": [
                            "Microsoft.Fabric.Capacity.State",
                            "Microsoft.Fabric.Capacity.Summary",
                        ],
                        "filters": [],
                    },
                }
                new_input_node = {"name": name}
            new_sources.append(new_source)
            new_input_nodes.append(new_input_node)
            ## Operation Events
            filtered_data = list(
                filter(
                    lambda table: 
                        table.get("properties", {}).get("capacityId") == capacity_id 
                        and table.get("type") == "FabricCapacityOperationEvents",
                    sources,
                )
            )
            if len(filtered_data) > 0:
                new_source = filtered_data.pop()
                new_input_node = {"name": new_source.get("name")}
            else:
                new_source = {
                    "id": str(uuid.uuid4()),
                    "name": f"{name}-operation",
                    "type": "FabricCapacityOperationEvents",
                    "properties": {
                        "eventScope": "Capacity",
                        "capacityId": capacity_id,
                        "includedEventTypes": [
                            "Microsoft.Fabric.CapacityOperationEvents.Operation"
                        ],
                        "filters": [],
                    },
                }
                new_input_node = {"name": name}
            new_sources.append(new_source)
            new_input_nodes.append(new_input_node)

        content["sources"] = new_sources

        for stream in content["streams"]:
            if stream["type"] == "DefaultStream":
                stream["inputNodes"] = new_input_nodes

    with open(property_file, "w", encoding="utf-8") as file:
        json.dump(content, file, indent=4)

    run_fab_command(
        f"import  /{workspace}.Workspace/{item_name}.Eventstream -i {tmp_path}/{item_name}.Eventstream -f ",
        silently_continue=True,
    )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

update_capcity_events_eventstream(workspace_name)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }
