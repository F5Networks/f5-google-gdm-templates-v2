#  expectValue = "Successful"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 180


TMP_DIR=/tmp/<DEWPOINT JOB ID>
STATE_FILE=${TMP_DIR}/state.json
PASSWORD=<AUTOFILL PASSWORD>

if [[ <PROVISION PUBLIC IP> == True ]]; then
    IP=$(cat ${STATE_FILE} | jq -r '.mgmtAddress')
    echo "IP: ${IP}"
    IP2=$(cat ${STATE_FILE} | jq -r '.mgmtAddress2')
    echo "IP: ${IP2}"
    RESPONSE=$(sshpass -p $PASSWORD ssh -o StrictHostKeyChecking=no admin@${IP} "bash -c 'cat /var/log/cloud/bigIpRuntimeInit.log | grep \"All operations finished successfully\"'")
    RESPONSE2=$(sshpass -p $PASSWORD ssh -o StrictHostKeyChecking=no admin@${IP2} "bash -c 'cat /var/log/cloud/bigIpRuntimeInit.log | grep \"All operations finished successfully\"'")
else
    BASTION_IP=$(cat ${STATE_FILE} | jq -r '.proxyAddress')
    IP=$(cat ${STATE_FILE} | jq -r '.mgmtAddress')
    IP2=$(cat ${STATE_FILE} | jq -r '.mgmtAddress2')
    echo "BASTION_IP: ${BASTION_IP}"
    echo "IP: ${IP}"
    echo "IP: ${IP2}"
    RESPONSE=$(ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -o ConnectTimeout=7 -i /etc/ssl/private/dewpt_private.pem -W %h:%p dewpt@${BASTION_IP}" admin@"${IP}" "bash -c 'cat /var/log/cloud/bigIpRuntimeInit.log | grep \"All operations finished successfully\"'")
    RESPONSE2=$(ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -o ConnectTimeout=7 -i /etc/ssl/private/dewpt_private.pem -W %h:%p dewpt@${BASTION_IP}" admin@"${IP2}" "bash -c 'cat /var/log/cloud/bigIpRuntimeInit.log | grep \"All operations finished successfully\"'")
fi

if echo $RESPONSE  | grep -Eq "All operations finished successfully"; then
    echo "IP ADDRESS: ${IP} is onboarded. Incrementing test counter..."
    ((count=count+1))
fi
if echo $RESPONSE2  | grep -Eq "All operations finished successfully"; then
    echo "IP ADDRESS: ${IP2} is onboarded. Incrementing test counter..."
    ((count=count+1))
fi
echo "Test counter: ${count}"

if [[ $count == 2 ]]; then
    echo "Successful"
fi