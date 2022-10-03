#  expectValue = "Success"
#  expectFailValue = "Failure"
#  scriptTimeout = 1
#  replayEnabled = false

TMP_DIR=/tmp/<DEWPOINT JOB ID>
STATE_FILE=${TMP_DIR}/state.json

# source test functions
source ${TMP_DIR}/test_functions.sh

case "<PROVISION PUBLIC IP>" in
  "False")
    IP=$(get_mgmt_ip <INSTANCE NAME> <AVAILABILITY ZONE BIGIP 1> private)
    IP2=$(get_mgmt_ip <INSTANCE NAME2> <AVAILABILITY ZONE BIGIP 2> private)

    BASTION_IP=$(gcloud compute instances describe <UNIQUESTRING>-bastion-vm-01 --zone <AVAILABILITY ZONE> --format json | jq -r '.networkInterfaces[].accessConfigs[]?|select (.name=="External NAT")|.natIP')
    APP_IP=$(get_app_ip <STACK NAME> <AVAILABILITY ZONE> private)
    APP_IP_INTERNAL=$(get_app_ip <STACK NAME> <AVAILABILITY ZONE> private)
    ;;
  *)
    IP=$(get_mgmt_ip <INSTANCE NAME> <AVAILABILITY ZONE BIGIP 1> public)
    IP2=$(get_mgmt_ip <INSTANCE NAME2> <AVAILABILITY ZONE BIGIP 2> public)
    BASTION_IP=''
    APP_IP=$(get_app_ip <INSTANCE NAME> <AVAILABILITY ZONE BIGIP 1> public)
    APP_IP_INTERNAL=$(get_app_ip <UNIQUESTRING>-application-vm-01 <AVAILABILITY ZONE> private)
    ;;
esac


# update state file
set_state "mgmtAddress" "$IP"
if [[ -n "$IP2" ]]; then
    set_state "mgmtAddress2" "$IP2"
fi

if [ -n "$BASTION_IP" ]; then
    set_state "proxyRequired" "true"
    set_state "proxyAddress" "$BASTION_IP"
else
    set_state "proxyRequired" "false"
    set_state "proxyAddress" ""
fi

set_state "applicationAddress" "$APP_IP"
set_state "applicationAddressInternal" "$APP_IP_INTERNAL"

echo "State file -"
cat ${STATE_FILE}

echo "Success"