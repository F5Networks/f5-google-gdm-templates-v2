#  expectValue = "Successful Traffic Test"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 60

TMP_DIR=/tmp/<DEWPOINT JOB ID>
STATE_FILE=${TMP_DIR}/state.json

# source test functions
source ${TMP_DIR}/test_functions.sh


if [[ "<PROVISION DEMO APP>" == "False" ]]; then
    echo "Successful Traffic Test"
else
    FW_RULE1=$(get_fr_ip <UNIQUESTRING>-fwrule1 <REGION>)
    FW_RULE2=$(get_fr_ip <UNIQUESTRING>-fwrule2 <REGION>)

    # echo "Application IP: $APP_IP"
    echo "Forwarding Rule 1 IP: $FW_RULE1"
    echo "Forwarding Rule 2 IP: $FW_RULE2"
    ## Curl IP for response
    if [[ -n "$FW_RULE1" && -n "$FW_RULE2" ]]; then
        response=$(curl http://$FW_RULE1 && curl http://$FW_RULE2)
    fi
    echo "Response: $response"

    if echo $response | grep "Demo App"; then
        echo "Successful Traffic Test"
    fi
fi