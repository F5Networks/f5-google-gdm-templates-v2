#  expectValue = "done"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 0

printf 'yes' | gcloud compute instance-groups managed delete <UNIQUESTRING>-bigip-ig --region <REGION>
