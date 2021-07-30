#  expectValue = "Succeeded"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 60

# SSH login for <ADMIN USERNAME> is set when we provision the instances, the actual admin user password is configured by runtime init
TMP_DIR=/tmp/<DEWPOINT JOB ID>
STATE_FILE=${TMP_DIR}/state.json

# source test functions
source ${TMP_DIR}/test_functions.sh
PASSWORD='<SECRET VALUE>'
MGMT_PORT='8443'
SSH_PORT='22'

INSTANCE1=$(gcloud compute instance-groups list-instances autoscale-<DEWPOINT JOB ID>-igm --zone=<AVAILABILITY ZONE> --format json | jq -r .[0].instance)
IP1=$(get_mgmt_ip ${INSTANCE1} <AVAILABILITY ZONE> public)
echo "IP1: ${IP1}"

PASSWORD_RESPONSE=$(curl -skvvu admin:${PASSWORD} https://${IP1}:${MGMT_PORT}/mgmt/tm/auth/user/admin | jq -r .description)
echo "PASSWORD_RESPONSE: ${PASSWORD_RESPONSE}"

if echo ${PASSWORD_RESPONSE} | grep -q "Admin User"; then
    IP1_LOGIN='Succeeded'
else
    IP1_LOGIN='Failed'
fi

INSTANCE2=$(gcloud compute instance-groups list-instances autoscale-<DEWPOINT JOB ID>-igm --zone=<AVAILABILITY ZONE> --format json | jq -r .[1].instance)
IP2=$(get_mgmt_ip ${INSTANCE2} <AVAILABILITY ZONE> public)
echo "IP2: ${IP2}"

PASSWORD_RESPONSE=$(curl -skvvu admin:${PASSWORD} https://${IP2}:${MGMT_PORT}/mgmt/tm/auth/user/admin | jq -r .description)
echo "PASSWORD_RESPONSE: ${PASSWORD_RESPONSE}"

if echo ${PASSWORD_RESPONSE} | grep -q "Admin User"; then
    IP2_LOGIN='Succeeded'
else
    IP2_LOGIN='Failed'
fi

if [[ ${IP1_LOGIN} == "Succeeded" && ${IP2_LOGIN} == "Succeeded" ]]; then
    echo 'Succeeded'
else
    echo 'Failed'
fi
