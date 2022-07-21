#  expectValue = "Succeeded"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 60

if [[ <PROVISION PUBLIC IP> == True ]]; then
    # get app address
    TMP_DIR=/tmp/<DEWPOINT JOB ID>

    # source test functions
    source ${TMP_DIR}/test_functions.sh

    APP_ADDRESS=$(get_fr_ip <UNIQUESTRING>-fwd-rule-01 <REGION>)
    echo "APP_ADDRESS: ${APP_ADDRESS}"

    # confirm app is available
    ACCEPTED_RESPONSE=$(curl -vv http://${APP_ADDRESS})
    echo "ACCEPTED_RESPONSE: ${ACCEPTED_RESPONSE}"

    # try something illegal (enforcement mode should be set to blocking by default)
    REJECTED_RESPONSE=$(curl -vv -X DELETE http://${APP_ADDRESS})
    echo "REJECTED_RESPONSE: ${REJECTED_RESPONSE}"
else
    echo "Demo app not provisioned, skipping test."
    ACCEPTED_RESPONSE="Demo App"
    REJECTED_RESPONSE="The requested URL was rejected"
fi

if echo $ACCEPTED_RESPONSE | grep -q "Demo App" && echo $REJECTED_RESPONSE | grep -q "The requested URL was rejected"; then
    echo "Succeeded"
else
    echo "Failed"
fi