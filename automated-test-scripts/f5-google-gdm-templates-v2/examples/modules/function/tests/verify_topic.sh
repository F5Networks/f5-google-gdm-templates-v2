#  expectValue = "TOPIC CREATION PASSED"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 3


response=$(gcloud pubsub topics list --format=json | jq .[].name)

if echo $response | grep topic-<DEWPOINT JOB ID> ; then
    echo "TOPIC CREATION PASSED"
fi