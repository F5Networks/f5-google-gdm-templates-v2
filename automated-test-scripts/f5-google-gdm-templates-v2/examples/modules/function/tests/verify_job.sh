#  expectValue = "JOB CREATION PASSED"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 3


response=$(gcloud scheduler jobs list --location <REGION> --format=json | jq .[].name)

if echo $response | grep job-<DEWPOINT JOB ID> ; then
    echo "JOB CREATION PASSED"
fi