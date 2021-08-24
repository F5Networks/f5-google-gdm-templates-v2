#  expectValue = "Successful"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 180

vms_ip_addresses=$(gcloud compute instances list --filter="name~'<UNIQUESTRING>'" --format=json | jq .[].networkInterfaces[].accessConfigs[].natIP | tr -d '"')
count=0

for ip_address in $vms_ip_addresses
do
    response=$(sshpass -p <TEST_ADMIN_PASSWORD> ssh -o StrictHostKeyChecking=no admin@${ip_address} "bash -c 'cat /var/log/cloud/bigIpRuntimeInit.log | grep \"All operations finished successfully\"'")
    if echo $response  | grep -Eq "All operations finished successfully"; then
        echo "IP ADDRESS: ${ip_address} is onboarded. Incrementing test counter..."
        ((count=count+1))
    fi
done

echo "Test counter: ${count}"

if [[ $count == <SCALING MIN> ]]; then
    echo "Successful"
fi
