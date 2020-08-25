# Utilities-and-Operations-Scripts

List of scripts used to manage the ESCAPE Datalake.
Those scripts are either executed manually or run periodically as cron jobs.

The synchronization with CRIC and IAM run inside a dedicated container in the Kubernetes cluster.

The scripts to update the proxies run on CERN LXPLUS service as acron jobs under afkiaras account.

The noise producing and gfal sam testing scripts run on LXPLUS as well but should be moved inside a dedicated container or platform.
