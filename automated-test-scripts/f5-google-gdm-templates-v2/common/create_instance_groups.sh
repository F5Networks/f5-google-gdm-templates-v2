#  expectValue = "Created"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0

gcloud compute instance-groups managed create <UNIQUESTRING>-bigip-ig \
    --base-instance-name <STACK NAME> \
    --size 1 \
    --template test-instance-template-1 \
    --region <REGION>
