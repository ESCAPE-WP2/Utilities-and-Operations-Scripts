#!/bin/bash

export X509_USER_PROXY=/afs/cern.ch/user/a/afkiaras/proxies/x509_escape
cd /afs/cern.ch/user/a/afkiaras/gfal_sam/
python /afs/cern.ch/user/a/afkiaras/gfal_sam/gfal_sam.py
