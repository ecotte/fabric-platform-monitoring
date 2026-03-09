# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "jupyter",
# META     "jupyter_kernel_name": "python3.11"
# META   }
# META }

# MARKDOWN ********************

# # Microsoft Fabric — Spark Live Monitoring 360
# ## Lab Guide
# 
# > **Level: Advanced**
# 
# *Centralize every Spark event, surface intelligent recommendations, and answer real-time performance questions through a conversational AI agent — all inside Microsoft Fabric.*
# 
# > **⚠️ Note:** This solution uses the **Diagnostic Emitter** extension to stream Spark events to Eventstream. It requires a **Custom Pool** and is not supported on the Starter Pool today.
# 
# ---
# 
# ## What You Will Build
# 
# By the end of this module you will have a live system that can answer:
# 
# | Question | Answered By |
# |---|---|
# | How many vCores are available right now? | Real-Time KQL Dashboard |
# | Which 10 notebooks consumed the most time today? | KQL Dashboard + Data Agent |
# | Will adding more executors actually improve performance? | Spark Recommender (Amdahl's Law) |
# | Are there task skews in my jobs? | Spark Recommender (Skew Detection) |
# | How do I improve the performance of a specific job? | Fabric Recommender |
# 
# ---
# 
# ## Architecture Overview
# 
# ```
# ┌──────────────────────────┐
# │   Spark Workloads         │   Notebooks · Spark Job Definitions
# │   (Any Fabric Workspace)  │   attached to monitored Environment
# └────────────┬─────────────┘
#              │  Spark events emitted via Environment config
#              ▼
# ┌──────────────────────────┐
# │      Eventstream          │   SparkMonitoring
# │   (Fabric Ingestion)      │   Real-time event routing
# └────────────┬─────────────┘
#              │
#              ▼
# ┌──────────────────────────┐
# │   Eventhouse / KQL DB     │   fabric-spark-monitoring
# │   (Central Store)         │   All raw Spark telemetry
# └────────┬─────────┬────────┘
#          │         │
#     ┌────▼───┐  ┌──▼──────────────────┐     ┌─────────────────────┐
#     │  KQL   │  │  Spark Recommender  │────▶│    Eventhouse        │
#     │  Live  │  │  Notebook (Python)  │     │  (writes results)    │
#     │  Dash  │  │                     │◀────│                      │
#     └────────┘  │  • Weighted heuristics    └─────────────────────┘
#                 │  • Amdahl's Law scaling
#                 │  • Skew detection
#                 │  • Anti-pattern scoring
#                 └─────────────┬───────────┘
#                               │
#                               ▼
#                 ┌─────────────────────────┐
#                 │   Fabric Spark Advisor   │
#                 │   Data Agent             │
#                 │   Natural language Q&A   │
#                 │   over all KQL tables    │
#                 └─────────────────────────┘
# ```
# 
# ---
# 
# ## Section 00 — Setup & Installation
# **⏱ Estimated time: 5 minutes**
# 
# ### Step 1 — Configure and Run the Setup Notebook
# 
# Open `Fabric Spark Monitoring Setup` notebook and set your workspace and environment IDs:
# 
# ```python
# environments = [
#     {
#         "workspace_id": "<your-workspace-id>",
#         "environment_id": "<your-environment-id>"
#     },
# ]
# ```
# > **No Spark jobs yet?** Pass the environment ID of the **Vasa Spark Simulator** environment.
# > The setup notebook will automatically inject the required Spark configs into your environment,
# > so any Notebook or Spark Job Definition attached to it starts streaming events to Eventstream immediately.
# 
# ---
# 
# 
# ### Step 2 — What Gets Deployed
# 
# Running the setup notebook provisions all required Fabric artifacts automatically:
# 
# | Artifact | Display Name | Type |
# |---|---|---|
# | Eventhouse | `fabric-spark-monitoring` | Eventhouse |
# | KQL Database | `Spark Monitoring` | KQL Database |
# | Eventstream | `SparkMonitoring` | Eventstream |
# | Recommender Notebook | `Spark Monitoring Recommendations` | Notebook |
# | Orchestration Pipeline | `SparkLensPipeline` | Data Pipeline |
# | Dashboard | `Spark Monitoring` | KQL Dashboard |
# | Data Agent | `Fabric Spark Advisor` | Data Agent |
# 
# ---


# CELL ********************

%pip install fabric-deployment-tool --quiet
%pip install semantic-link-labs --quiet

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

# MARKDOWN ********************

# 
# ### Step 3 — Generate Sample Telemetry (Optional)
# **⏱ Estimated time: 60 minutes**
# 
# If you do not have existing Spark workloads, run the **Vasa Spark Simulator** pipeline inside `spark-simulator` folder to generate realistic telemetry across 30+ job patterns:
# 
# 1. Attach the `vasa-spark-simulator` Fabric Environment to the simulator pipeline
# 2. Run the **Vasa Simulator Pipeline** — this executes 30+ Notebook runs covering anti-patterns, performance issues, and best practices
# 3. All events stream automatically into Eventstream → Eventhouse
# 
# ---
# 
# ### Step 4 — Populate the Recommendations Tables
# **⏱ Estimated time: 10 minutes**
# 
# Run **SparkLensPipeline** to process the raw telemetry through the recommender engine.
# 
# | Table | Contains | Primary Use |
# |---|---|---|
# | `sparklens_metrics` | Numeric metrics per app (efficiency, GC, skew, duration) | Dashboard + ranking queries |
# | `sparklens_recommendations` | SparkLens findings per app with severity + fixes | Recommender output |
# | `fabric_recommendations` | Fabric config recommendations (NEE, VOrder, etc.) | Best practice validation |
# | `sparklens_metadata` | All Spark config properties per app | Config audit |
# | `sparklens_predictions` | Amdahl's Law scaling estimates | Capacity planning |
# | `sparklens_summary` | Stage-level task statistics | Deep-dive diagnostics |
# | `SparkRecommenderFeedback` | User ratings on recommendations | Continuous improvement |
# 
# ---
# 
# ## Section 01 — Real-Time Dashboard
# **⏱ Estimated time: 20 minutes**
# 
# > **What you will see:** Live vCore utilization, top 10 notebooks by duration,
# > executor vs. driver time split across all running jobs.
# 
# ---
# 
# ### Spark Recommender
# 
# > **What you will see:** Each application classified by bottleneck type,
# > with specific config recommendations and scaling predictions.
# 
# #### How the Recommender Works
# 
# The recommender uses **weighted heuristic scoring** — no labeled training data required.
# 
# ```
# Performance Score = (ExecutorEfficiency × 30)
#                   + (ParallelismScore  × 30)
#                   + ((1 − GCOverhead)  × 20)
#                   + ((1 / SkewRatio)   × 20)
# ```
# 
# | Score | Label | Recommended Action |
# |---|---|---|
# | 80 – 100 | ✅ EXCELLENT | Monitor only |
# | 65 – 79 | 🟡 GOOD | Minor tuning |
# | 50 – 64 | 🟠 FAIR | Moderate action needed |
# | < 50 | 🔴 POOR | Immediate action required |
# 
# #### Amdahl's Law Scaling Predictions
# 
# For every application the recommender answers: **"Will adding more executors actually help?"**
# 
# ```
# Predicted speedup = 1 / (DriverTimeFraction + (ExecutorTimeFraction / N))
# 
# Where N = executor multiplier (0.25x, 0.5x, 1x, 1.5x, 2x, 4x)
# ```
# 
# ---
# 
# ## Section 03 — Fabric Spark Advisor (Data Agent)
# 
# > **What you will see:** Natural language Q&A over all Spark telemetry.
# > No KQL expertise required.
# 
# ### What You Can Ask
# 
# **Performance analysis:**
# ```
# Analyze application_1771441543262_0001
# Show me all driver-heavy jobs
# Will adding more executors help application_177..._0001?
# ```
# 
# The Data Agent reads directly from Eventhouse — every answer is backed by your actual telemetry:
# 
# ---


# MARKDOWN ********************

# 
# ## Troubleshooting
# 
# **Events not appearing in Eventhouse**
# → Confirm the monitored Environment is attached to the Notebook or SJD before running
# 
# **Data Agent returns "no data found"**
# → Confirm SparkLensPipeline has run at least once after simulator execution
# 
# ---
