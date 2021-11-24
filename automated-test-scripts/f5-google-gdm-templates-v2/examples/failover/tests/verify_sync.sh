#  expectValue = "SUCCESS"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 5


FLAG='FAIL'
TMP_DIR=/tmp/<DEWPOINT JOB ID>
STATE_FILE=${TMP_DIR}/state.json
PASSWORD=<AUTOFILL PASSWORD>


if [[ <PROVISION PUBLIC IP> == False ]]; then
    echo 'MGMT PUBLIC IP IS NOT ENABLED'
    BASTION_IP=$(cat ${STATE_FILE} | jq -r '.proxyAddress')
    IP=$(cat ${STATE_FILE} | jq -r '.mgmtAddress')
    IP2=$(cat ${STATE_FILE} | jq -r '.mgmtAddress2')
    echo "BASTION_IP: ${BASTION_IP}"
    echo "IP: ${IP}"
    echo "IP: ${IP2}"

    BIGIP1_SSH_RESPONSE=$(sshpass -p ${PASSWORD} ssh -o "StrictHostKeyChecking no" -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p dewpt@$BASTION_IP" admin@${IP} "tmsh show cm sync-status")
    echo "BIGIP1_SSH_RESPONSE: ${BIGIP1_SSH_RESPONSE}"
    BIGIP2_SSH_RESPONSE=$(sshpass -p ${PASSWORD} ssh -o "StrictHostKeyChecking no" -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p dewpt@$BASTION_IP" admin@${IP2} "tmsh show cm sync-status")
    echo "BIGIP2_RESPONSE: ${BIGIP2_SSH_RESPONSE}"

else
    echo 'MGMT PUBLIC IP IS ENABLED'
    IP=$(cat ${STATE_FILE} | jq -r '.mgmtAddress')
    IP2=$(cat ${STATE_FILE} | jq -r '.mgmtAddress2')
    echo "IP: ${IP}"
    echo "IP: ${IP2}"

    BIGIP1_SSH_RESPONSE=$(sshpass -p ${PASSWORD} ssh -o "StrictHostKeyChecking no" admin@${IP} "tmsh show cm sync-status")
    echo "BIGIP1_SSH_RESPONSE: ${BIGIP1_SSH_RESPONSE}"
    BIGIP2_SSH_RESPONSE=$(sshpass -p ${PASSWORD} ssh -o "StrictHostKeyChecking no" admin@${IP2} "tmsh show cm sync-status")
    echo "BIGIP2_RESPONSE: ${BIGIP2_SSH_RESPONSE}"
fi


# evaluate responses
if echo ${BIGIP1_SSH_RESPONSE} | grep -q "high-availability" && echo ${BIGIP2_SSH_RESPONSE} | grep -q "high-availability" && echo ${BIGIP1_SSH_RESPONSE} | grep -q "All devices in the device group are in sync" && echo ${BIGIP2_SSH_RESPONSE} | grep -q "All devices in the device group are in sync"; then
    FLAG='SUCCESS'
fi

echo $FLAG