#  expectValue = "done"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0

network_gcloud=$(gcloud compute networks list --format json | jq -r --arg n "<DEWPOINT JOB ID>" '.[] | select(.name | contains($n)) | .name')

gcloud="gcloud compute firewall-rules create "
gcloud+="<UNIQUESTRING>-firewall "
gcloud+="--allow tcp:80,tcp:22,tcp:443,tcp:8443 "
gcloud+="--network=$network_gcloud --source-ranges=0.0.0.0/0"
$gcloud