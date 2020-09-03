#!/bin/bash

export HOMEPATH="/afs/cern.ch/user/r/rdimaria"
export LOCALPATH="${HOMEPATH}/gfal_sam/"
export CRIC_URL="http://escape-cric.cern.ch/api/doma/rse/query/?json&preset=doma"

cd $LOCALPATH
export X509_USER_PROXY=${HOMEPATH}/proxies/x509up_escape

python gfal_sam.py