#  expectValue = "Successful"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 3

tP=$(gcloud compute target-pools list --filter="name~'<UNIQUESTRING>-bigip-tp'" --format=json | jq .[0])


if [[ ! -z $tP ]]; then
    echo "Successful"
fi
