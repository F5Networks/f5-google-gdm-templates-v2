#  expectValue = "Succeeded"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 60

TMP_DIR='/tmp/<DEWPOINT JOB ID>'
STATE_FILE=${TMP_DIR}/state.json

# source test functions
source ${TMP_DIR}/test_functions.sh
PASSWORD='<SECRET VALUE>'
MGMT_PORT='8443'
SSH_PORT='22'

INSTANCE1=$(gcloud compute instance-groups list-instances <UNIQUESTRING>-bigip-igm --zone=<AVAILABILITY ZONE> --format json | jq -r .[0].instance)
INSTANCE2=$(gcloud compute instance-groups list-instances <UNIQUESTRING>-bigip-igm --zone=<AVAILABILITY ZONE> --format json | jq -r .[1].instance)
if [[ <PROVISION PUBLIC IP> == True ]]; then
    IP1=$(get_mgmt_ip ${INSTANCE1} <AVAILABILITY ZONE> public)
    IP2=$(get_mgmt_ip ${INSTANCE2} <AVAILABILITY ZONE> public)
    echo "IP1: ${IP1}"
    echo "IP2: ${IP2}"

    RESPONSE1=$(ssh -o "StrictHostKeyChecking=no" -o ConnectTimeout=7 -i /etc/ssl/private/dewpt_private.pem admin@"$IP1" "cat /var/log/restnoded/restnoded.log | grep '[telemetry.Google_Cloud_Monitoring.Google_Cloud_Monitoring_Namespace::My_Consumer] success'")
    RESPONSE2=$(ssh -o "StrictHostKeyChecking=no" -o ConnectTimeout=7 -i /etc/ssl/private/dewpt_private.pem admin@"$IP1" "cat /var/log/restnoded/restnoded.log | grep '[telemetry.Google_Cloud_Monitoring.Google_Cloud_Monitoring_Namespace::My_Consumer] success'")
else
    if [ "<BASTION AUTOSCALE>" == "False" ]; then
        echo "STANDALONE CASE"
        BASTION_IP=$(get_bastion_ip <UNIQUESTRING>-bastion <AVAILABILITY ZONE> public)
    else
        echo "AUTOSCALE CASE"
        INSTANCE=$(get_instance_group_instances <UNIQUESTRING>-bastion-igm <AVAILABILITY ZONE>)
        echo "INSTANCE: $INSTANCE"
        BASTION_IP=$(get_bastion_ip $INSTANCE <AVAILABILITY ZONE> public)
    fi

    IP1=$(get_mgmt_ip ${INSTANCE1} <AVAILABILITY ZONE> private)
    IP2=$(get_mgmt_ip ${INSTANCE2} <AVAILABILITY ZONE> private)
    echo "IP1: ${IP1}"
    echo "IP2: ${IP2}"
    echo "BASTION_IP: ${BASTION_IP}"

    RESPONSE1=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p dewpt@${BASTION_IP}" admin@"${IP1}" "cat /var/log/restnoded/restnoded.log | grep '[telemetry.Google_Cloud_Monitoring.Google_Cloud_Monitoring_Namespace::My_Consumer] success'")
    RESPONSE2=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p dewpt@${BASTION_IP}" admin@"${IP2}" "cat /var/log/restnoded/restnoded.log | grep '[telemetry.Google_Cloud_Monitoring.Google_Cloud_Monitoring_Namespace::My_Consumer] success'")
fi

echo "RESPONSE1: ${RESPONSE1}"
echo "RESPONSE2: ${RESPONSE2}"

if echo ${RESPONSE1} | grep -q "success" && echo ${RESPONSE2} | grep -q "success"; then
    echo 'Succeeded'
else
    echo 'Failed'
fi
