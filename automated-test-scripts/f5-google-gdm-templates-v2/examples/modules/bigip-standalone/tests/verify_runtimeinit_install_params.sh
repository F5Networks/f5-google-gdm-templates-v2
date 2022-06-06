#  expectValue = "SUCCESS"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 5


TMP_DIR=/tmp/<DEWPOINT JOB ID>
STATE_FILE=${TMP_DIR}/state.json

# source test functions
source ${TMP_DIR}/test_functions.sh

IP=$(cat ${STATE_FILE} | jq -r '.mgmtAddress')
IP2=$(cat ${STATE_FILE} | jq -r '.mgmtAddress2')
BASTION_IP=$(cat ${STATE_FILE} | jq -r '.proxyAddress')
PASSWORD=$(gcloud compute instances describe <UNIQUESTRING>-<INSTANCE NAME> --zone=<AVAILABILITY ZONE> --format json | jq -r .id)
response=$(sshpass -p $PASSWORD ssh -o StrictHostKeyChecking=no admin@${IP} "bash -c 'cat /config/cloud/telemetry_install_params.tmp'")

if echo $response  | grep "/examples/modules/bigip-standalone/bigip_standalone.py"; then
    echo "SUCCESS"
fi

