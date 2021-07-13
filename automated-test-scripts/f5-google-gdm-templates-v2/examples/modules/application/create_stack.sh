#  expectValue = "completed successfully"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0

template_url=<TEMPLATE URL>
echo "template_url = $template_url"
template_file=$(basename "$template_url")
echo "template_file = $template_file"
tmpl_file="/tmp/$template_file"
echo "tmpl_file = $tmpl_file"
rm -f $tmpl_file

curl -k $template_url -o $tmpl_file

networkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<DEWPOINT JOB ID>-network1" '.[] | select(.name | contains($n)) | .selfLink')
subnetSelfLink=$(gcloud compute networks subnets list --format json | jq -r --arg n "<DEWPOINT JOB ID>-subnet1" '.[] | select(.name | contains($n)) | .selfLink')

# Run GDM Application template
properties="appContainerName:'<APP CONTAINER NAME>',createAutoscaleGroup:<AUTOSCALE>,availabilityZone:'<AVAILABILITY ZONE>',hostname:'<HOST NAME>',instanceType:'<INSTANCE TYPE>',uniqueString:'<UNIQUESTRING>',networkSelfLink:'$networkSelfLink',subnetSelfLink:'$subnetSelfLink'"
echo $properties
gcloud deployment-manager deployments create <STACK NAME> --template $tmpl_file --labels "delete=true" --properties $properties

# clean up file on disk
rm -f $tmpl_file