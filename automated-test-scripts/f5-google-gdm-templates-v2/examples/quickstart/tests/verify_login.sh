#  expectValue = "Succeeded"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 60

# SSH login for <ADMIN USERNAME> is set when we provision the instances, the actual admin user password is configured by runtime init
TMP_DIR=/tmp/<DEWPOINT JOB ID>
STATE_FILE=${TMP_DIR}/state.json

# source test functions
source ${TMP_DIR}/test_functions.sh

IP1=$(cat ${STATE_FILE} | jq -r '.mgmtAddress')
IP2=$(cat ${STATE_FILE} | jq -r '.mgmtAddress2')
BASTION_IP=$(cat ${STATE_FILE} | jq -r '.proxyAddress')

PASSWORD='<UNIQUESTRING>-bigip1'
if [[ <NUMBER NICS> -gt 1 ]]; then
    MGMT_PORT='443'
else
    MGMT_PORT='8443'
fi

PASSWORD_RESPONSE=$(curl -skvvu quickstart:${PASSWORD} https://${IP1}:${MGMT_PORT}/mgmt/tm/auth/user/quickstart | jq -r .description)
echo "PASSWORD_RESPONSE: ${PASSWORD_RESPONSE}"

if echo ${PASSWORD_RESPONSE} | grep -q "quickstart"; then
    echo 'Succeeded'
else
    echo 'Failed'
fi
