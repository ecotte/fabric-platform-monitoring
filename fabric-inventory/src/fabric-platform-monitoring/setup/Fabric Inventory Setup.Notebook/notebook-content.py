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

%pip install semantic-link-labs==0.13.2 --quiet

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# MARKDOWN ********************

# # ✅ Prerequisites for Fabric Inventory & Fabric Admin API
# 
# This document outlines the required setup to successfully run the **Fabric Inventory** process using the **Microsoft Fabric Admin API**.
# 
# ---
# 
# ## 🔐 1. Service Principal with Fabric Admin Permissions
# 
# To access the **Microsoft Fabric Admin API**, authentication must be performed using a **service principal (SP)** with **administrator-level permissions**.
# 
# **Key points:**
# - The Fabric Admin API is restricted to **Fabric administrators** only.
# - The service principal must be explicitly granted **Fabric admin rights**.
# - The relevant **Fabric admin settings** must allow service principal access.
# 
# 📘 Refer to the **Fabric admin settings documentation** for the authoritative configuration details.
# 
# ---
# 
# ## 🗝️ 2. Azure Key Vault for Credential Management
# 
# An **Azure Key Vault** is required to securely store the credentials used by the process.
# 
# The Key Vault must contain the following secrets:
# - **Tenant ID**
# - **Service Principal (Application) ID**
# - **Service Principal Secret**
# 
# ✅ Using Key Vault ensures:
# - No credentials are hardcoded in notebooks or pipelines  
# - Centralized and auditable secret management  
# - Improved security and compliance  
# 
# ---
# 
# ## 👤 3. Permissions for the Execution Identity
# 
# The **user or identity executing the Fabric Inventory process** must have permission to read secrets from the Key Vault.
# 
# **Minimum required access:**
# - Ability to retrieve secrets at runtime
# - Typically granted via the **Key Vault Secrets User** role (or equivalent)
# 
# Without this access, authentication will fail even if the service principal is correctly configured.
# 
# ---
# 
# ## 📓 4. Notebook Configuration (Required)
# 
# The notebooks include a **configuration cell** that must be updated to reference the Key Vault.
# 
# You must modify the variables in this cell to specify:
# - **Azure Key Vault URI**
# - **Secret name** for the Tenant ID
# - **Secret name** for the Service Principal ID
# - **Secret name** for the Service Principal Secret
# 
# These values allow the notebook to dynamically retrieve credentials from Key Vault during execution.
# 
# ---
# 
# ## ▶️ 5. Enable the Pipeline Schedule
# 
# Once all prerequisites and configurations are in place:
# 
# - Enable the **pipeline schedule** associated with the Fabric Inventory process
# - The scheduled pipeline will automatically start and run the process based on the defined cadence
# 
# No additional manual steps are required after the schedule is enabled.
# 
# ---
# 
# ## 🧠 Why This Setup Matters
# 
# This configuration ensures:
# - ✅ Secure, non-interactive authentication
# - ✅ Compliance with Fabric Admin API security requirements
# - ✅ No exposure of sensitive credentials
# - ✅ Reliable, automated execution of the Fabric Inventory process
# 
# ---
# 
# ## ✅ Final Checklist
# 
# Before enabling the pipeline schedule, confirm the following:
# 
# - ✔️ Service principal has **Fabric Admin API access**
# - ✔️ Azure Key Vault contains **Tenant ID, SP ID, and SP Secret**
# - ✔️ Executing identity can **read Key Vault secrets**
# - ✔️ Notebook variables are correctly set with **Key Vault details**
# - ✔️ Pipeline schedule is **enabled**
# 
# 🚀 Once completed, the Fabric Inventory process will run automatically as scheduled.


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

variable_library_name = "Fabric Platform Monitoring"
kql_db_name = "Platform Inventory"

kqldb = labs.kql_database.list_kql_databases()
kqldb = kqldb[kqldb["KQL Database Name"] == kql_db_name]

labs.variable_library.update_variable(variable_library=variable_library_name,name="kusto_query_uri",value=kqldb['Query Service URI'].iloc[0])
labs.variable_library.update_variable(variable_library=variable_library_name,name="kusto_ingest_uri",value=kqldb['Ingestion Service URI'].iloc[0])
labs.variable_library.update_variable(variable_library=variable_library_name,name="key_vault_uri",value=key_vault_uri)
labs.variable_library.update_variable(variable_library=variable_library_name,name="key_vault_tenant_id",value=key_vault_tenant_id)
labs.variable_library.update_variable(variable_library=variable_library_name,name="key_vault_client_id",value=key_vault_client_id	)
labs.variable_library.update_variable(variable_library=variable_library_name,name="key_vault_client_secret",value=key_vault_client_secret)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }
