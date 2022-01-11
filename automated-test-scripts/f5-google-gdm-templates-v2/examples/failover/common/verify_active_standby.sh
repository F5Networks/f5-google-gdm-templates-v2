#  expectValue = "SUCCESS"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 20

FLAG='FAIL'
TMP_DIR=/tmp/<DEWPOINT JOB ID>
STATE_FILE=${TMP_DIR}/state.json
PASSWORD=<AUTOFILL PASSWORD>
IP=$(cat ${STATE_FILE} | jq -r '.mgmtAddress')
IP2=$(cat ${STATE_FILE} | jq -r '.mgmtAddress2')
echo "IP: ${IP}"
echo "IP: ${IP2}"


if [[ <PROVISION PUBLIC IP> == False ]]; then
    echo 'MGMT PUBLIC IP IS NOT ENABLED'
    BASTION_IP=$(cat ${STATE_FILE} | jq -r '.proxyAddress')
    echo "BASTION_IP: ${BASTION_IP}"

    state=$(sshpass -p ${PASSWORD} ssh -o "StrictHostKeyChecking no" -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p dewpt@$BASTION_IP" admin@${IP} "tmsh show sys failover")
    state2=$(sshpass -p ${PASSWORD} ssh -o "StrictHostKeyChecking no" -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p dewpt@$BASTION_IP" admin@${IP2} "tmsh show sys failover")

else
    echo 'MGMT PUBLIC IP IS ENABLED'

    state=$(sshpass -p ${PASSWORD} ssh -o "StrictHostKeyChecking no" admin@${IP} "tmsh show sys failover")
    state2=$(sshpass -p ${PASSWORD} ssh -o "StrictHostKeyChecking no" admin@${IP2} "tmsh show sys failover")
fi


echo "State: $state"
echo "State2: $state2"

# evaluate result
if echo $state | grep 'active' && echo $state2 | grep 'standby'; then
    echo "SUCCESS"
elif echo $state2 | grep 'active' && echo $state | grep 'standby'; then
    echo "SUCCESS"
fi
