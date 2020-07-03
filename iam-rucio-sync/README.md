# Syncing IAM ESCAPE Users to the ESCAPE Rucio instance

## How to use:

1) Configure iam-config.conf or set up the Environment Variables to point to the correct IAM Server and provide your Client ID and Secret
2) You run the script on a place that the Rucio server is installed and the Rucio database configure on the rucio.cfg

## Example
    $ export IAM_SERVER=https://iam-escape.cloud.cnaf.infn.it
    $ export IAM_CLIENT_ID=my_client_id
    $ export IAM_CLIENT_SECRET=my_secret

    $ python sync_iam_rucio.py

