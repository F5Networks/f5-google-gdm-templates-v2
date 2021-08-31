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
    IP=$(get_mgmt_ip <UNIQUESTRING>-<INSTANCE NAME> <AVAILABILITY ZONE> private)
    if [[ "<TEMPLATE URL>" == *"failover"* ]] && [[ "<AVAILABILITY ZONE2>" == "<REGION>-c" ]]; then
        IP2=$(get_mgmt_ip <STACK NAME> <AVAILABILITY ZONE2> private)
    elif [[ "<TEMPLATE URL>" == *"failover"* ]] && [[ "<AVAILABILITY ZONE2>" != "<REGION>-c" ]]; then
        IP2=$(get_mgmt_ip <STACK NAME> <AVAILABILITY ZONE> private)        
    else
        IP2=''
    fi
    # TODO: hardcoded bastion host - in us-west-1 until bastion host creation
    # along with the test can be automated
    BASTION_IP=$(gcloud compute instances describe <UNIQUESTRING>-bastion --zone <AVAILABILITY ZONE> --format json | jq -r '.networkInterfaces[].accessConfigs[]?|select (.name=="External NAT")|.natIP')
    APP_IP=$(get_app_ip <STACK NAME> <AVAILABILITY ZONE> private)
    APP_IP_INTERNAL=$(get_app_ip <STACK NAME> <AVAILABILITY ZONE> private)
    ;;
  *)
    IP=$(get_mgmt_ip <UNIQUESTRING>-<INSTANCE NAME> <AVAILABILITY ZONE> public)
    if [[ "<TEMPLATE URL>" == *"failover"* ]] && [[ "<AVAILABILITY ZONE2>" == "<REGION>-c" ]]; then
        IP2=$(get_mgmt_ip <STACK NAME> <AVAILABILITY ZONE2> public)
    elif [[ "<TEMPLATE URL>" == *"failover"* ]] && [[ "<AVAILABILITY ZONE2>" != "<REGION>-c" ]]; then
        IP2=$(get_mgmt_ip <STACK NAME> <AVAILABILITY ZONE> public)        
    else
        IP2=''
    fi
    BASTION_IP=''
    if [[ <NUMBER NICS> -gt 1 ]]; then
        APP_IP=$(get_app_ip <UNIQUESTRING>-<INSTANCE NAME> <AVAILABILITY ZONE> public)
    else
        APP_IP=$(get_mgmt_ip <UNIQUESTRING>-<INSTANCE NAME> <AVAILABILITY ZONE> public)
    fi
    APP_IP_INTERNAL=$(get_app_ip <UNIQUESTRING>-app <AVAILABILITY ZONE> private)
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