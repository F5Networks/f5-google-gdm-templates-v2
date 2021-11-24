#  expectValue = "Successful"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 30

instance_status=$(gcloud compute instances list --filter="name~'<INSTANCE NAME>'" --format=json | jq .[].status | tr -d '"' )
instance_status2=$(gcloud compute instances list --filter="name~'<INSTANCE NAME2>'" --format=json | jq .[].status | tr -d '"' )

count=0
for status in $instance_status
do
    [[ $status == 'RUNNING' ]] && (( count=count + 1 ))
done

for status in $instance_status2
do
    [[ $status == 'RUNNING' ]] && (( count=count + 1 ))
done

if [[ $count == 2 ]]; then
    echo "Successful"
fi
