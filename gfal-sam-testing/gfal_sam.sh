#!/bin/bash

export LOCALPATH="/afs/cern.ch/user/r/ridona/escape/wp2-github/Utilities-and-Operations-Scripts/gfal-sam-testing/gfal_sam/"

/usr/bin/voms-proxy-init -voms escape
export X509_USER_PROXY=/tmp/x509up_u127450

mkdir -p $LOCALPATH
/usr/bin/python /afs/cern.ch/user/r/ridona/escape/wp2-github/Utilities-and-Operations-Scripts/gfal-sam-testing/gfal_sam.py
