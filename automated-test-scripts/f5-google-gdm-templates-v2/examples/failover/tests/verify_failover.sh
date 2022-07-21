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

    state=$(sshpass -p ${PASSWORD} ssh -o "StrictHostKeyChecking no" -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p dewpt@${BASTION_IP}" admin@${IP} "tmsh show sys failover")
    echo "State: $state"
    active=$(echo $state |grep active)

    case $active in
    active)
      echo "Current State: $active , nothing to do, grab bigip-vm-02 status"
      result=$(sshpass -p ${PASSWORD} ssh -o "StrictHostKeyChecking no" -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p dewpt@${BASTION_IP}" admin@${IP2} "tmsh show sys failover")  ;;
    *)
      echo "Current State: $active , setting system to standby on bigip-vm-02"
      sshpass -p ${PASSWORD} ssh -o "StrictHostKeyChecking no" -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p dewpt@${BASTION_IP}" admin@${IP2} "tmsh run sys failover standby"
      result=$(sshpass -p ${PASSWORD} ssh -o "StrictHostKeyChecking no" -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p dewpt@${BASTION_IP}" admin@${IP2} "tmsh show sys failover")  ;;
    esac
else
    echo 'MGMT PUBLIC IP IS ENABLED'

    state=$(sshpass -p ${PASSWORD} ssh -o "StrictHostKeyChecking no" admin@${IP} "tmsh show sys failover")
    echo "State: $state"
    active=$(echo $state |grep active)

    case $active in
    active)
      echo "Current State: $active , nothing to do, grab bigip-vm-02 status"
      result=$(sshpass -p ${PASSWORD} ssh -o "StrictHostKeyChecking no" admin@${IP2} "tmsh show sys failover")  ;;
    *)
      echo "Current State: $active , setting system to standby on bigip-vm-02"
      sshpass -p ${PASSWORD} ssh -o "StrictHostKeyChecking no" admin@${IP2} "tmsh run sys failover standby"
      result=$(sshpass -p ${PASSWORD} ssh -o "StrictHostKeyChecking no" admin@${IP2} "tmsh show sys failover")  ;;
    esac
fi



# evaluate result
if echo $result | grep 'Failover standby'; then
    echo "SUCCESS"
else
    echo "FAILED"
fi
