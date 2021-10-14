#  expectValue = "SUCCESS"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 5

count=0
vms_ip_addresses=$(gcloud compute instances list --filter="name~'<UNIQUESTRING>'" --format=json | jq .[].networkInterfaces[].accessConfigs[].natIP | tr -d '"')

echo "BIGIP Public IPs: $vms_ip_addresses"

for ip_address in $vms_ip_addresses
do
    SSH_RESPONSE=$(sshpass -p <TEST_ADMIN_PASSWORD> ssh -o StrictHostKeyChecking=no admin@${ip_address} "bash -c 'cat /config/cloud/telemetry_install_params.tmp'")
    if echo $SSH_RESPONSE | grep "/examples/modules/bigip-autoscale/bigip_autoscale.py"; then
        echo "IP ADDRESS: ${ip_address} has install parameters stored on disk. Incrementing test counter..."
        ((count=count+1))
    fi
done

echo "Test counter: ${count}"

if [[ $count == <SCALING MIN> ]]; then
    echo "SUCCESS"
fi
