#!/bin/bash
secret="-s node1-c1.srv.example.com -pw ***"
PUPPETHOST=root@puppetca.example.com

# select the current server as deployment server and his storage-repository
VMSR=`xe $secret sr-list host=${VMHOST} name-label='Local storage' --minimal`
VMUUID=`xe $secret vm-install template=${TMPLUUID} new-name-label=${VMNAME} sr-uuid=${VMSR}`
echo "Generating and fetching certificate"

ssh ${PUPPETHOST} "puppetca --generate $VMNAME.$VMDM"
PUP_PUB=$(${PUPPETHOST} "base64 -w0 /var/lib/puppet/ssl/ca/signed/$VMNAME.$VMDM.pem")
PUP_PRV=$(${PUPPETHOST} "base64 -w0 /var/lib/puppet/ssl/private_keys/$VMNAME.$VMDM.pem")
# dont fuck around below this

xe $secret vif-create vm-uuid=${VMUUID} network-uuid=$NETWORKUUID mac=random device=0
xe $secret vm-param-set uuid=${VMUUID} xenstore-data:vm-data/ip=$VMIP
xe $secret vm-param-set uuid=${VMUUID} xenstore-data:vm-data/gw=$VMGW
xe $secret vm-param-set uuid=${VMUUID} xenstore-data:vm-data/nm=$VMMASK
xe $secret vm-param-set uuid=${VMUUID} xenstore-data:vm-data/ns=$VMNS
xe $secret vm-param-set uuid=${VMUUID} xenstore-data:vm-data/dm=$VMDM

#xe $secret vm-param-set uuid=${VMUUID} xenstore-data:vm-data/puppet/ca=$PUP_CA
xe $secret vm-param-set uuid=${VMUUID} xenstore-data:vm-data/puppet/pub=$PUP_PUB
xe $secret vm-param-set uuid=${VMUUID} xenstore-data:vm-data/puppet/prv=$PUP_PRV

xe $secret vm-param-set uuid=${VMUUID} PV-args='-- console=hvc0'
xe $secret vm-start uuid=${VMUUID}

