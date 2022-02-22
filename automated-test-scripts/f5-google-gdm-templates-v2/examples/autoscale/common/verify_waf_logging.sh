#  expectValue = "Succeeded"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 60


RESPONSE=$(gcloud logging read "resource.type=generic_node AND logName=projects/<PROJECT>/logs/<LOG ID> AND jsonPayload.request_status=blocked" --limit 1 --format json | jq -r .[].jsonPayload.attack_type)

if echo $RESPONSE | grep -q "Leakage"; then
    echo "Succeeded"
else
    echo "Failed"
fi