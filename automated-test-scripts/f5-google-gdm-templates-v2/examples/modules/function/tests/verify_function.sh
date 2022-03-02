#  expectValue = "FUNCTION CREATION PASSED"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 3

response=$(gcloud functions list --format json | jq .[].name)

if echo $response | grep func-<DEWPOINT JOB ID> ; then
    echo "FUNCTION CREATION PASSED"
fi