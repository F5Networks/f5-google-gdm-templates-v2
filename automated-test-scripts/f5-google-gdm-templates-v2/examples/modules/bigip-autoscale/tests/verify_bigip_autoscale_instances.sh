#  expectValue = "Successful"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 30
vms_status=$(gcloud compute instances list --filter="name~'<UNIQUESTRING>'" --format=json | jq .[].status | tr -d '"' )

count=0
for status in $vms_status
do
    [[ $status == 'RUNNING' ]] && (( count=count + 1 ))
done

if [[ $count == <SCALING MIN> ]]; then
    echo "Successful"
fi
