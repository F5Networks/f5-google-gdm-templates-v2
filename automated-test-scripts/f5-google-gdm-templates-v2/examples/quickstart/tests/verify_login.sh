#  expectValue = "Succeeded"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 60


# SSH login for <ADMIN USERNAME> is set when we provision the instances, the actual admin user password is configured by runtime init
TMP_DIR=/tmp/<DEWPOINT JOB ID>

# source test functions
source ${TMP_DIR}/test_functions.sh

if [[ <NUMBER NICS> -gt 1 ]]; then
    MGMT_PORT='443'
else
    MGMT_PORT='8443'
fi

instance_id=$(gcloud compute instances list --filter="name~'<UNIQUESTRING>-<INSTANCE NAME>'" --format=json | jq -r .[].id )

PASSWORD=$instance_id

if [[ <PROVISION PUBLIC IP> == True ]]; then
    IP=$(get_mgmt_ip <UNIQUESTRING>-bigip1 <AVAILABILITY ZONE> public)
    echo "IP: ${IP}"
    ssh-keygen -R $IP 2>/dev/null
    PASSWORD_RESPONSE=$(curl -skvvu quickstart:${PASSWORD} https://${IP}:${MGMT_PORT}/mgmt/tm/auth/user/quickstart | jq -r .description)
else
    BASTION_IP=$(get_bastion_ip <UNIQUESTRING>-bastion <AVAILABILITY ZONE>)
    IP=$(get_mgmt_ip <UNIQUESTRING>-bigip1 <AVAILABILITY ZONE> private)
    echo "BASTION_IP: ${BASTION_IP}"
    echo "IP: ${IP}"
    ssh-keygen -R $BASTION_IP 2>/dev/null
    PASSWORD_RESPONSE=$(ssh -o "StrictHostKeyChecking=no" -o ConnectTimeout=7 -i /etc/ssl/private/dewpt_private.pem dewpt@"$BASTION_IP" "curl -skvvu quickstart:${PASSWORD} https://${IP}:${MGMT_PORT}/mgmt/tm/auth/user/quickstart")
fi
echo "PASSWORD_RESPONSE: ${PASSWORD_RESPONSE}"

if echo ${PASSWORD_RESPONSE} | grep -q "quickstart"; then
    echo 'Succeeded'
else
    echo 'Failed'
fi
