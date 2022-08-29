#  expectValue = "Successful Test"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 30

TMP_DIR=/tmp/<DEWPOINT JOB ID>
STATE_FILE=${TMP_DIR}/state.json

# source test functions
source ${TMP_DIR}/test_functions.sh
if [ "<AUTOSCALE>" == "False" ]; then
    echo "DO STANDALONE"
    BASTION_IP=$(get_bastion_ip <UNIQUESTRING>-bastion-vm-01 <AVAILABILITY ZONE> public)
else
    echo "DO AUTOSCALE"
    INSTANCE=$(gcloud compute instance-groups list-instances <UNIQUESTRING>-bastion-igm --region=<REGION> --format json | jq -r .[0].instance | cut -d'/' -f11)
    echo "INSTANCE: $INSTANCE"
    BASTION_IP=$(get_bastion_ip $INSTANCE <AVAILABILITY ZONE> public)
fi

echo "Bastion IP: $BASTION_IP"
## Curl IP for response
if [ -n "$BASTION_IP" ]; then
    response=$(ssh -o "StrictHostKeyChecking=no" -o ConnectTimeout=7 -i /etc/ssl/private/dewpt_private.pem dewpt@"$BASTION_IP" "cat /etc/motd")
fi
echo "Response: $response"

if echo $response | grep "Welcome to Bastion Host"; then
    echo "Successful Test"
fi
