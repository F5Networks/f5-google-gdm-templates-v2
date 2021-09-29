#  expectValue = "Successful"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 30

instance_status=$(gcloud compute instances list --filter="name~'<UNIQUESTRING>-<INSTANCE NAME>'" --format=json | jq .[].status | tr -d '"' )

count=0
for status in $instance_status
do
    [[ $status == 'RUNNING' ]] && (( count=count + 1 ))
done

if [[ $count == 1 ]]; then
    echo "Successful"
fi
