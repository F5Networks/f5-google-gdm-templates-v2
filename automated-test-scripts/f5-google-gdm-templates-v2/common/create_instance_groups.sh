#  expectValue = "Created"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0

gcloud compute instance-groups managed create <STACK NAME>-ig \
    --base-instance-name <STACK NAME> \
    --size 2 \
    --template test-instance-template-1 \
    --region <REGION>
