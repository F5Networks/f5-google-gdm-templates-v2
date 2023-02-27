#  expectValue = "Deleted"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 0

gcloud compute instance-groups managed delete <UNIQUESTRING>-bigip-ig --region <REGION> -q
