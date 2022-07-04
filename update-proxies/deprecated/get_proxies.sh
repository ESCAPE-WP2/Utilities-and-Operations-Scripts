#!/bin/bash

HOMEPATH="/afs/cern.ch/user/r/rdimaria"

cd ${HOMEPATH}/proxies
voms-proxy-init --cert escape_cern_xrdcert.pem --key escape_cern_xrdkey.pem --out x509up_escape --voms escape