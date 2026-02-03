# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "jupyter",
# META     "jupyter_kernel_name": "python3.11"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

%pip install ms-fabric-cli --quiet

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# MARKDOWN ********************

# # Define Properties

# CELL ********************

HeartbeatEnable = True
HeartbeatInterval = 1
ReportSendInterval = 5
ReportRetention = 10
TenatId = ""
AppId = ""

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# MARKDOWN ********************

# # Load Libraries

# CELL ********************

import subprocess
import yaml
import sempy.fabric as fabric
import json

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# MARKDOWN ********************

# # Variables

# CELL ********************

heartbeat_eventsteam = "GatewayMonitoringHeartbeat.Eventstream"
report_eventstream = "GatewayMonitoringReports.Eventstream"

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# MARKDOWN ********************

# ## Definition of deployment functions

# CELL ********************

# Set environment parameters for Fabric CLI
token = notebookutils.credentials.getToken('pbi')
os.environ['FAB_TOKEN'] = token
os.environ['FAB_TOKEN_ONELAKE'] = token

def run_fab_command( command, capture_output: bool = False, silently_continue: bool = False):
    result = subprocess.run(["fab", "-c", command], capture_output=capture_output, text=True)
    if (not(silently_continue) and (result.returncode > 0 or result.stderr)):
       raise Exception(f"Error running fab command. exit_code: '{result.returncode}'; stderr: '{result.stderr}'")    
    if (capture_output): 
        output = result.stdout.strip()
        return output

def fab_get_id(name):
    id = run_fab_command(f"get /{workspace_name}.Workspace/{name} -q id" , capture_output = True, silently_continue= True)
    return(id)

def fab_get_item(name):
    item = run_fab_command(f"get /{workspace_name}.Workspace/{name}" , capture_output = True, silently_continue= True)
    return(item)

def fab_list_item():
    items = run_fab_command(f"ls /{workspace_name}.Workspace" , capture_output = True, silently_continue= True)
    return(items)

def fab_get_display_name(name):
    display_name = run_fab_command(f"get /{workspace_name}.Workspace/{name} -q displayName" , capture_output = True, silently_continue= True)
    return(display_name)

def fab_get_kusto_query_uri(name):
    connection = run_fab_command(f"get /{workspace_name}.Workspace/{name} -q properties.queryServiceUri", capture_output = True, silently_continue= True)
    return(connection)

def fab_get_kusto_ingest_uri(name):
    connection = run_fab_command(f"get /{workspace_name}.Workspace/{name} -q properties.ingestionServiceUri", capture_output = True, silently_continue= True)
    return(connection)

def fab_get_folders():
    response = run_fab_command(f"api workspaces/{workspace_id}/folders", capture_output = True, silently_continue= True)
    return(json.loads(response).get('text',{}).get('value',[]))

def fab_get_folder(folder_name):
    for f in fab_get_folders():
        if f.get('displayName') == folder_name:
            return f
    return None

def fab_assign_item_folder(item_id,folder):
    folder_details = fab_get_folder(folder)

    if folder_details is None:
        payload = json.dumps({"displayName": folder})
        folder_details = run_fab_command(f"api -X post workspaces/{workspace_id}/folders -i {payload}", capture_output = True, silently_continue= True)
        folder_details = json.loads(folder_details).get('text',{})

    payload = json.dumps({"folder": folder_details.get('id')})

    return run_fab_command(f"api -X patch workspaces/{workspace_id}/items/{item_id} -i {payload}", capture_output = True, silently_continue= True)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# MARKDOWN ********************

# ## Get current Workspace
# This cell gets the current workspace to deploy FUAM automatically inside it

# CELL ********************

workspace_id = fabric.get_notebook_workspace_id()
workspace_name = fabric.list_workspaces(filter=f"id eq '{workspace_id}'")['Name'][0]

heartbeat_id = fab_get_id(heartbeat_eventsteam)
report_id = fab_get_id(report_eventstream)

heartbeat_conn_id = json.loads(run_fab_command(f"api workspaces/{workspace_id}/eventstreams/{heartbeat_id}/topology" , capture_output = True, silently_continue= True)).get("text",{}).get("sources",[])[0].get('id')
report_conn_id = json.loads(run_fab_command(f"api workspaces/{workspace_id}/eventstreams/{report_id}/topology" , capture_output = True, silently_continue= True)).get("text",{}).get("sources",[])[0].get('id')

heartbeat_connection = json.loads(run_fab_command(f"api workspaces/{workspace_id}/eventstreams/{heartbeat_id}/sources/{heartbeat_conn_id}/connection" , capture_output = True, silently_continue= True)).get("text",{}).get('accessKeys',{}).get('primaryConnectionString')
report_connection = json.loads(run_fab_command(f"api workspaces/{workspace_id}/eventstreams/{report_id}/sources/{report_conn_id}/connection" , capture_output = True, silently_continue= True)).get("text",{}).get('accessKeys',{}).get('primaryConnectionString')

GatewayLogUploadConfig = {
    "GatewayId": "",
    "GatewayLogsPath": ["C:\Windows\ServiceProfiles\PBIEgwService\AppData\Local\Microsoft\On-premises data gateway"],      
    "RootPath": "raw",
    "OutputPath": ".\data",
    "HeartbeatEnable": HeartbeatEnable,
    "HeartbeatInterval": HeartbeatInterval,
    "ReportSendInterval": ReportSendInterval,
    "ReportRetention": ReportRetention,
    "VerboseLogSendInterval": 600,
    "ServicePrincipal": {
        "TennatId": TenatId,
        "AppId": AppId,
        "SecretText": "",
    },
    "EventHubs": {
        "UploadReports": True,
        "ConnectionStrings": [
                {
                        "Report": "Heartbeat",
                        "EventHubConnectionString": heartbeat_connection
                },
                {
                        "Report": "Reports",
                        "EventHubConnectionString": report_connection
                }
        ]
    },
    "Lakehouse": {
        "UploadReports": False,
        "UploadLogs": False,
        "WorkspaceName": "",
        "LakehouseName": "",        
    },
    "ConnectionProperties": {
        "MaximumRetryCount": 3,
        "RetryIntervalSec": 1
    }
}

out_file = open("./builtin/config.json", "w")

json.dump(obj=GatewayLogUploadConfig,fp=out_file,indent=6)

out_file.close()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }
