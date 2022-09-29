#  expectValue = "Succeeded"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 30

TMP_DIR='/tmp/<DEWPOINT JOB ID>'
STATE_FILE=${TMP_DIR}/state.json

# source test functions
source ${TMP_DIR}/test_functions.sh
PASSWORD='<SECRET VALUE>'
MGMT_PORT='8443'
SSH_PORT='22'

INSTANCE1=$(gcloud compute instance-groups list-instances <UNIQUESTRING>-bigip-igm --region=<REGION> --format json | jq -r .[0].instance)
INSTANCE2=$(gcloud compute instance-groups list-instances <UNIQUESTRING>-bigip-igm --region=<REGION> --format json | jq -r .[1].instance)
if [[ <PROVISION PUBLIC IP> == True ]]; then
    IP1=$(get_mgmt_ip ${INSTANCE1} <AVAILABILITY ZONE 1> public)
    IP2=$(get_mgmt_ip ${INSTANCE2} <AVAILABILITY ZONE 2> public)
    echo "IP1: ${IP1}"
    echo "IP2: ${IP2}"

    RESPONSE1=$(ssh -o "StrictHostKeyChecking=no" -o ConnectTimeout=7 -i /etc/ssl/private/dewpt_private.pem admin@"$IP1" "bash -c 'cat /var/log/restnoded/restnoded.log'")
    RESPONSE2=$(ssh -o "StrictHostKeyChecking=no" -o ConnectTimeout=7 -i /etc/ssl/private/dewpt_private.pem admin@"$IP2" "bash -c 'cat /var/log/restnoded/restnoded.log'")
else
    if [ "<BASTION AUTOSCALE>" == "False" ]; then
        echo "STANDALONE CASE"
        BASTION_IP=$(get_bastion_ip <UNIQUESTRING>-bastion <AVAILABILITY ZONE> public)
    else
        echo "AUTOSCALE CASE"
        INSTANCE=$(gcloud compute instance-groups list-instances <UNIQUESTRING>-bastion-igm --region=<REGION> --format json | jq -r .[].instance)
        echo "INSTANCE: $INSTANCE"
        BASTION_IP=$(get_bastion_ip $INSTANCE <AVAILABILITY ZONE> public)
    fi

    IP1=$(get_mgmt_ip ${INSTANCE1} <AVAILABILITY ZONE 1> private)
    IP2=$(get_mgmt_ip ${INSTANCE2} <AVAILABILITY ZONE 2> private)
    echo "IP1: ${IP1}"
    echo "IP2: ${IP2}"
    echo "BASTION_IP: ${BASTION_IP}"

    RESPONSE1=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p dewpt@${BASTION_IP}" admin@"${IP1}" "bash -c 'cat /var/log/restnoded/restnoded.log'")
    RESPONSE2=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p dewpt@${BASTION_IP}" admin@"${IP2}" "bash -c 'cat /var/log/restnoded/restnoded.log'")
fi

echo "RESPONSE1: ${RESPONSE1}"
echo "RESPONSE2: ${RESPONSE2}"

if echo ${RESPONSE1} | grep -q "Pipeline processed data of type: ASM" && echo ${RESPONSE2} | grep -q "Pipeline processed data of type: ASM"; then
    echo 'Succeeded'
else
    echo 'Failed'
fi
