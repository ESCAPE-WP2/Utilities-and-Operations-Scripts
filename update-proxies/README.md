Follow the acron CERN documentation to set up a cron job on aiadm that runs every 12 hours https://acrondocs.web.cern.ch/. 

$ acron jobs create -s '* */12 * * *' -t lxplus.cern.ch -c 'bash /afs/cern.ch/user/e/egazzarr/private/clusters/escape-gitops/proxies/update_proxies.sh' -d 'Update robot client proxies'

This will generate the voms proxy every 12 hours and inject it in to the pod of each daemon and create to rucio secrtes, one in the rucio namespace and the other in the crons namespace. 