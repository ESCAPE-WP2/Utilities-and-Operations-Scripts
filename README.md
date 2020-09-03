# Utilities-and-Operations-Scripts

The scripts are used to manage the ESCAPE DataLake, and are either executed manually or run periodically as cron jobs.

The synchronizations with CRIC and IAM run inside a dedicated deployment in the Kubernetes cluster.

The scripts to update the proxies run on CERN LXPLUS/AIADM service as acron jobs under rdimaria account.

The noise producing and gfal sam testing scripts run on LXPLUS as well but should be moved inside a dedicated container or platform.