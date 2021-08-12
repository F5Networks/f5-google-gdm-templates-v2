#  expectValue = "Successful"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 180


TMP_DIR=/tmp/<DEWPOINT JOB ID>
STATE_FILE=${TMP_DIR}/state.json

# source test functions
source ${TMP_DIR}/test_functions.sh

IP=$(cat ${STATE_FILE} | jq -r '.mgmtAddress')
IP2=$(cat ${STATE_FILE} | jq -r '.mgmtAddress2')
BASTION_IP=$(cat ${STATE_FILE} | jq -r '.proxyAddress')

response=$(sshpass -p <UNIQUESTRING>-<INSTANCE NAME> ssh -o StrictHostKeyChecking=no quickstart@${IP} "bash -c 'cat /var/log/cloud/bigIpRuntimeInit.log | grep \"All operations finished successfully\"'")
if echo $response  | grep -Eq "All operations finished successfully"; then
    echo "IP ADDRESS: ${IP} is onboarded. Incrementing test counter..."
    ((count=count+1))
fi


echo "Test counter: ${count}"

if [[ $count == 1 ]]; then
    echo "Successful"
fi