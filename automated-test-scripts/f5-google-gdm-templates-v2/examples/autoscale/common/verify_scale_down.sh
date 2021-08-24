#  expectValue = "Succeeded"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 180

CAPACITY=$(gcloud compute instance-groups managed describe <UNIQUESTRING>-bigip-igm --zone=<AVAILABILITY ZONE> --format json | jq -r .targetSize)
echo "CAPACITY: ${CAPACITY}"

# Check that only one device is present in the scale set
if [[ $CAPACITY == "1" ]]; then
     echo "Succeeded"
fi
