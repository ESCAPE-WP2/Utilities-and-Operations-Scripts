#!/bin/bash

HOMEPATH="/afs/cern.ch/user/r/rdimaria"
KUBERNETESCLUSTER="${HOMEPATH}/escape-gitops/"

RELEASENAMEDAEMONS="escape-daemons"

# Propagates proxy to FTS and Kubernetes Cluster
export X509_USER_PROXY=${HOMEPATH}/proxies/x509up_escape

export KUBECONFIG=${KUBERNETESCLUSTER}/escape-gitops_config
cd ${KUBERNETESCLUSTER}
cp ${X509_USER_PROXY} x509up
for OUTPUT in $(kubectl -n rucio get pods | cut -d " " -f1 | grep daemons)
do
    echo $OUTPUT
    kubectl -n rucio cp x509up $OUTPUT:/x509up
done
kubectl delete secret ${RELEASENAMEDAEMONS}-rucio-x509up -n rucio
kubectl create secret generic ${RELEASENAMEDAEMONS}-rucio-x509up --from-file=x509up -n rucio
#scp /afs/cern.ch/user/a/afkiaras/proxies/x509up_escape root@escape-jupyter-lab-rucio:/root/x509up
ssh lxplus fts-delegation-init -s https://fts3-pilot.cern.ch:8446 --proxy ${X509_USER_PROXY}