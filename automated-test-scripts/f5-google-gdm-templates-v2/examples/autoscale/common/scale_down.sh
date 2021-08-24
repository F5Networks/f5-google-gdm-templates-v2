#  expectValue = "Succeeded"
#  expectFailValue = "Failed"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 30

SCALE_DOWN=$(gcloud compute instance-groups managed update-autoscaling <UNIQUESTRING>-bigip-igm --max-num-replicas 1 --min-num-replicas 0 --zone=<AVAILABILITY ZONE> --format json | jq -r .[0].status)
echo "SCALE_DOWN: ${SCALE_DOWN}"

if [[ $SCALE_DOWN == "ACTIVE" ]]; then
    echo "Succeeded"
else
    echo "Failed"
fi
