#  expectValue = "Successful Traffic Test"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 10

TMP_DIR=/tmp/<DEWPOINT JOB ID>
STATE_FILE=${TMP_DIR}/state.json

# source test functions
source ${TMP_DIR}/test_functions.sh

APP_IP=$(get_app_ip <UNIQUESTRING>-application-py <AVAILABILITY ZONE> public)

echo "Application IP: $APP_IP"
## Curl IP for response
if [ -n "$APP_IP" ]; then
    response=$(curl http://$APP_IP)
fi
echo "Response: $response"

if echo $response | grep "Demo App"; then
    echo "Successful Traffic Test"
fi