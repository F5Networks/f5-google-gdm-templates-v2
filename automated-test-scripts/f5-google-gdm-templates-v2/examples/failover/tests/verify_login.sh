#  expectValue = "Succeeded"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 60


# SSH login for ADMIN is set when we provision the instances, the actual admin user password is configured by runtime init using supplied secret name
TMP_DIR=/tmp/<DEWPOINT JOB ID>
STATE_FILE=${TMP_DIR}/state.json

MGMT_PORT='443'

PASSWORD=<AUTOFILL PASSWORD>

if [[ <PROVISION PUBLIC IP> == True ]]; then
    IP=$(cat ${STATE_FILE} | jq -r '.mgmtAddress')
    echo "IP: ${IP}"
    IP2=$(cat ${STATE_FILE} | jq -r '.mgmtAddress2')
    echo "IP: ${IP2}"
    PASSWORD_RESPONSE=$(curl -skvvu admin:${PASSWORD} https://${IP}:${MGMT_PORT}/mgmt/tm/auth/user/admin)
    PASSWORD_RESPONSE2=$(curl -skvvu admin:${PASSWORD} https://${IP2}:${MGMT_PORT}/mgmt/tm/auth/user/admin)
else
    BASTION_IP=$(cat ${STATE_FILE} | jq -r '.proxyAddress')
    IP=$(cat ${STATE_FILE} | jq -r '.mgmtAddress')
    IP2=$(cat ${STATE_FILE} | jq -r '.mgmtAddress2')
    echo "BASTION_IP: ${BASTION_IP}"
    echo "IP: ${IP}"
    echo "IP: ${IP2}"
    PASSWORD_RESPONSE=$(ssh -o "StrictHostKeyChecking=no" -o ConnectTimeout=7 -i /etc/ssl/private/dewpt_private.pem dewpt@"$BASTION_IP" "curl -skvvu admin:${PASSWORD} https://${IP}:${MGMT_PORT}/mgmt/tm/auth/user/admin")
    PASSWORD_RESPONSE2=$(ssh -o "StrictHostKeyChecking=no" -o ConnectTimeout=7 -i /etc/ssl/private/dewpt_private.pem dewpt@"$BASTION_IP" "curl -skvvu admin:${PASSWORD} https://${IP2}:${MGMT_PORT}/mgmt/tm/auth/user/admin")
fi
echo "PASSWORD_RESPONSE: ${PASSWORD_RESPONSE}"
echo "PASSWORD_RESPONSE2: ${PASSWORD_RESPONSE2}"

if echo ${PASSWORD_RESPONSE} | grep -q "admin"; then
    echo "IP ADDRESS: ${IP} successfully logged into, incrementing test counter..."
    ((count=count+1))
fi
if echo ${PASSWORD_RESPONSE2} | grep -q "admin"; then
    echo "IP ADDRESS: ${IP2} successfully logged into, incrementing test counter..."
    ((count=count+1))
fi

echo "Test counter: ${count}"

if [[ $count == 2 ]]; then
    echo "Succeeded"
fi