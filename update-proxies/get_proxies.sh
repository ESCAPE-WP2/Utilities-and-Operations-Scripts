#!/bin/bash
cd /afs/cern.ch/user/a/afkiaras
printf 'REPLACE_CERTIFICATE_PASSWORD_HERE' | voms-proxy-init --voms escape --out /afs/cern.ch/user/a/afkiaras/proxies/x509_escape
printf 'REPLACE_CERTIFICATE_PASSWORD_HERE' | voms-proxy-init --voms dteam --out /afs/cern.ch/user/a/afkiaras/proxies/x509_dteam
