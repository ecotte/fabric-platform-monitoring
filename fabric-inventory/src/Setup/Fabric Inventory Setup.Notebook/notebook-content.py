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

%pip install semantic-link-labs --quiet

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

key_vault_uri = ""
key_vault_tenant_id = ""
key_vault_client_id = ""
key_vault_client_secret = ""

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

import sempy_labs as labs
import sempy_labs.variable_library as sempy_variable_library

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

variable_library_name = "Fabric Platform Monitoring"
kql_db_name = "Platform Inventory"

kqldb = labs.list_kql_databases()
kqldb = kqldb[kqldb["KQL Database Name"] == kql_db_name]

sempy_variable_library.update_variable(variable_library=variable_library_name,name="kusto_query_uri",value=kqldb['Query Service URI'].iloc[0])
sempy_variable_library.update_variable(variable_library=variable_library_name,name="kusto_ingest_uri",value=kqldb['Ingestion Service URI'].iloc[0])
sempy_variable_library.update_variable(variable_library=variable_library_name,name="key_vault_uri",value=key_vault_uri)
sempy_variable_library.update_variable(variable_library=variable_library_name,name="key_vault_tenant_id",value=key_vault_tenant_id)
sempy_variable_library.update_variable(variable_library=variable_library_name,name="key_vault_client_id",value=key_vault_client_id	)
sempy_variable_library.update_variable(variable_library=variable_library_name,name="key_vault_client_secret",value=key_vault_client_secret)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }
