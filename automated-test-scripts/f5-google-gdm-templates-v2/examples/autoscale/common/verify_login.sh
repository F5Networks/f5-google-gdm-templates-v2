#  expectValue = "Succeeded"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 60

# SSH login for <ADMIN USERNAME> is set when we provision the instances, the actual admin user password is configured by runtime init
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

    PASSWORD_RESPONSE1=$(curl -skvvu admin:${PASSWORD} https://${IP1}:${MGMT_PORT}/mgmt/tm/auth/user/admin | jq -r .description)
    PASSWORD_RESPONSE2=$(curl -skvvu admin:${PASSWORD} https://${IP2}:${MGMT_PORT}/mgmt/tm/auth/user/admin | jq -r .description)
    echo "PASSWORD_RESPONSE1: ${PASSWORD_RESPONSE1}"
    echo "PASSWORD_RESPONSE2: ${PASSWORD_RESPONSE2}"
else
    if [ "<BASTION AUTOSCALE>" == "False" ]; then
        echo "STANDALONE CASE"
        BASTION_IP=$(get_bastion_ip <UNIQUESTRING>-bastion <AVAILABILITY ZONE> public)
    else
        echo "AUTOSCALE CASE"
        # INSTANCE=$(get_instance_group_instances <UNIQUESTRING>-bastion-igm <AVAILABILITY ZONE>)
        INSTANCE=$(gcloud compute instance-groups list-instances <UNIQUESTRING>-bastion-igm --region=<REGION> --format json | jq -r .[].instance)
        echo "INSTANCE: $INSTANCE"
        BASTION_IP=$(get_bastion_ip $INSTANCE <AVAILABILITY ZONE> public)
    fi

    IP1=$(get_mgmt_ip ${INSTANCE1} <AVAILABILITY ZONE 1> private)
    IP2=$(get_mgmt_ip ${INSTANCE2} <AVAILABILITY ZONE 2> private)
    echo "IP1: ${IP1}"
    echo "IP2: ${IP2}"
    echo "BASTION_IP: ${BASTION_IP}"

    PASSWORD_RESPONSE1=$(ssh -o "StrictHostKeyChecking=no" -o ConnectTimeout=7 -i /etc/ssl/private/dewpt_private.pem dewpt@"$BASTION_IP" "curl -skvvu admin:${PASSWORD} https://${IP1}:${MGMT_PORT}/mgmt/tm/auth/user/admin")
    PASSWORD_RESPONSE2=$(ssh -o "StrictHostKeyChecking=no" -o ConnectTimeout=7 -i /etc/ssl/private/dewpt_private.pem dewpt@"$BASTION_IP" "curl -skvvu admin:${PASSWORD} https://${IP2}:${MGMT_PORT}/mgmt/tm/auth/user/admin")
    echo "PASSWORD_RESPONSE1: ${PASSWORD_RESPONSE1}"
    echo "PASSWORD_RESPONSE2: ${PASSWORD_RESPONSE2}"
fi


if echo ${PASSWORD_RESPONSE1} | grep -q "Admin User" && echo ${PASSWORD_RESPONSE2} | grep -q "Admin User"; then
    echo 'Succeeded'
else
    echo 'Failed'
fi
