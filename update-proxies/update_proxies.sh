#!/bin/sh

# this command makes sure that the script stops if something goes bad as everything runs in the background
set -e 

PROXYPATH="/afs/cern.ch/user/e/egazzarr/private/clusters/escape-gitops/proxies/"
RELEASENAMEDAEMONS="escape-daemons"

cd ${PROXYPATH}

# generating the robot client proxies
voms-proxy-init --cert ./client.crt --key ./client.key --out x509up_escape --voms escape

export X509_USER_PROXY="/afs/cern.ch/user/e/egazzarr/private/clusters/escape-gitops/proxies/x509up_escape"
export KUBECONFIG="/afs/cern.ch/user/e/egazzarr/private/clusters/escape-gitops/config"

# copying the robot client certificate in each daemon pod (had to exclude the automatic restart)
cp ${X509_USER_PROXY} x509up
for OUTPUT in $(kubectl -n rucio get pods | cut -d " " -f1 | grep daemons | grep -vw 'automatic')
do
    echo $OUTPUT
    kubectl -n rucio cp x509up $OUTPUT:/x509up
done

# rucio daemons x509_up secret
kubectl delete secret ${RELEASENAMEDAEMONS}-rucio-x509up -n rucio
kubectl create secret generic ${RELEASENAMEDAEMONS}-rucio-x509up --from-file=x509up -n rucio

# x509up for Crons
kubectl delete secret prod-rucio-x509up -n crons
kubectl create secret generic prod-rucio-x509up --from-file=x509up -n crons
kubectl delete secret prod-rucio-x509up
kubectl create secret generic prod-rucio-x509up --from-file=x509up
kubectl delete secret prod-rucio-x509up -n rucio
kubectl create secret generic prod-rucio-x509up --from-file=x509up -n rucio

#FTS delegation
ssh lxplus fts-delegation-init -s https://fts3-pilot.cern.ch:8446 --proxy ${X509_USER_PROXY}
exit 0
