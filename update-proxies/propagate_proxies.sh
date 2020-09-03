#!/bin/bash

HOMEPATH="/afs/cern.ch/user/r/rdimaria"
KUBERNETESCLUSTER="${HOMEPATH}/escape-wp2-k8s"

# Propagates proxy to FTS and Kubernetes Cluster
export X509_USER_PROXY=${HOMEPATH}/proxies/x509up_escape
eval $(ai-rc "ESCAPE WP2 CERN")
export KUBECONFIG=${KUBERNETESCLUSTER}/config
cd ${KUBERNETESCLUSTER}
cp ${X509_USER_PROXY} x509up
for OUTPUT in $(kubectl get pods | cut -d " " -f1 | grep daemons)
do
    echo $OUTPUT
    kubectl cp x509up $OUTPUT:/x509up
done
kubectl delete secret prod-rucio-x509up
kubectl create secret generic prod-rucio-x509up --from-file=x509up
#scp /afs/cern.ch/user/a/afkiaras/proxies/x509up_escape root@escape-jupyter-lab-rucio:/root/x509up
ssh lxplus6 fts-delegation-init -s https://fts3-pilot.cern.ch:8446 --proxy ${X509_USER_PROXY}