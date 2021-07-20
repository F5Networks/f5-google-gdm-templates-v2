#  expectValue = "Successful"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 3

tP=$(gcloud compute target-pools list --filter="name~'<STACK NAME>-tp'" --format=json | jq .[0])


if [[ ! -z $tP ]]; then
    echo "Successful"
fi
