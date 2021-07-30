#  expectValue = "Successful Traffic Test"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 30

TMP_DIR=/tmp/<DEWPOINT JOB ID>
STATE_FILE=${TMP_DIR}/state.json

# source test functions
source ${TMP_DIR}/test_functions.sh
if [ "<AUTOSCALE>" == "False" ]; then
    echo "DO STANDALONE"
    APP_IP=$(get_app_ip <UNIQUESTRING>-application <AVAILABILITY ZONE> public)
else
    echo "DO AUTOSCALE"
    INSTANCE=$(get_instance_group_instances <UNIQUESTRING>-application-igm <AVAILABILITY ZONE>)
    echo "INSTANCE: $INSTANCE"
    APP_IP=$(get_app_ip $INSTANCE <AVAILABILITY ZONE> public)
fi

echo "Application IP: $APP_IP"
## Curl IP for response
if [ -n "$APP_IP" ]; then
    response=$(curl http://$APP_IP)
fi
echo "Response: $response"

if echo $response | grep "Demo App"; then
    echo "Successful Traffic Test"
fi