#  expectValue = "Successful"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 3

mgmtFw=$(gcloud compute firewall-rules list --filter="name~'<UNIQUESTRING>-mgmtfw'" --format=json | jq .[0])
appFw=$(gcloud compute firewall-rules list --filter="name~'<UNIQUESTRING>-appvipfw'" --format=json | jq .[0])

# Validating that mgmtFw and appFw created as expected
if [[ ! -z $mgmtFw && ! -z $appFw ]]; then

    # Validating Allowed Ports for MGMT and APP firewalls
    allowedPortsMgmt=$(echo $mgmtFw | jq .allowed[0].ports[])
    allowedPortsApp=$(echo $appFw | jq .allowed[0].ports[])
    if echo $allowedPortsMgmt | grep '22' && echo $allowedPortsMgmt | grep '<MGMT PORT>' && echo $allowedPortsApp | grep '<APP PORT>'; then
        echo "Successful"
    fi
fi

