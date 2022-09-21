Follow the acron CERN documentation to set up a cron job on aiadm that runs every 8 hours https://acrondocs.web.cern.ch/. 

$ acron jobs create -s '0 */8 * * *' -t lxplus8.cern.ch -c 'bash /afs/cern.ch/user/e/egazzarr/private/clusters/escape-gitops/proxies/update_proxies.sh' -d 'Update robot client proxies'

This will generate the voms proxy every 8 hours and inject it in to the pod of each daemon and create the rucio secrtes, one in the rucio namespace and the other in the crons namespace. 
