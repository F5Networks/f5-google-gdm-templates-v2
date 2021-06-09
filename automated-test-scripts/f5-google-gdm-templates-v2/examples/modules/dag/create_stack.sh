#  expectValue = "completed successfully"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0


TMP_DIR="/tmp/<DEWPOINT JOB ID>"

# source test functions
source ${TMP_DIR}/test_functions.sh

# determine test environment public ip address
source_cidr=$(get_env_public_ip)
echo "source_cidr=$source_cidr"


template_url=<TEMPLATE URL>
echo "template_url = $template_url"
template_file=$(basename "$template_url")
echo "template_file = $template_file"
tmpl_file="/tmp/$template_file"
echo "tmpl_file = $tmpl_file"
rm -f $tmpl_file

curl -k $template_url -o $tmpl_file


externalNetworkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<DEWPOINT JOB ID>-network0" '.[] | select(.name | contains($n)) | .selfLink')
externalSubnetSelfLink=$(gcloud compute networks subnets list --format json | jq -r --arg n "<DEWPOINT JOB ID>-subnet0" '.[] | select(.name | contains($n)) | .selfLink')

mgmtNetworkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<DEWPOINT JOB ID>-network1" '.[] | select(.name | contains($n)) | .selfLink')
mgmtSubnetSelfLink=$(gcloud compute networks subnets list --format json | jq -r --arg n "<DEWPOINT JOB ID>-subnet1" '.[] | select(.name | contains($n)) | .selfLink')

internalNetworkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<DEWPOINT JOB ID>-network2" '.[] | select(.name | contains($n)) | .selfLink')
internalSubnetSelfLink=$(gcloud compute networks subnets list --format json | jq -r --arg n "<DEWPOINT JOB ID>-subnet2" '.[] | select(.name | contains($n)) | .selfLink')

optional_parm=',guiPortMgmt:<MGMT PORT>'

if [[ "<NUM INTERNAL FORWARDING RULES>" = 1 ]]; then
    optional_parm="${optional_parm},restrictedSrcAddressAppInternal:${source_cidr},applicationInternalPort:'<APP INTERNAL PORT>'"
fi

instances=()
response=$(gcloud compute instance-groups list-instances <STACK NAME>-ig --region <REGION> --format=json | jq .[].instance)
for item in $response
do
    instances+=($(echo ${item} | tr -d '"') )
done

instanceGroupSelfLink=$(gcloud compute instance-groups describe <STACK NAME>-ig --region <REGION> --format=json | jq .selfLink | tr -d '"')


# Run GDM Dag template
properties="region:'<REGION>',instances:[$instances],instance-groups:[$instanceGroupSelfLink],applicationPort:'<APP PORT>',networkSelfLinkInternal:'$internalNetworkSelfLink',subnetSelfLinkInternal:'$internalSubnetSelfLink',networkSelfLinkMgmt:'$mgmtNetworkSelfLink',subnetSelfLinkMgmt:'$mgmtSubnetSelfLink',networkSelfLinkExternal:'$externalNetworkSelfLink',subnetSelfLinkExternal:'$externalSubnetSelfLink',restrictedSrcAddressMgmt:${source_cidr},numberOfForwardingRules:<NUM FORWARDING RULES>,numberOfInternalForwardingRules:<NUM INTERNAL FORWARDING RULES>,restrictedSrcAddressApp:${source_cidr},restrictedSrcAddressAppInternal:${source_cidr},uniqueString:'<UNIQUESTRING>',applicationInternalPort:'<APP INTERNAL PORT>'${optional_parm}"
echo $properties

gcloud deployment-manager deployments create <STACK NAME> --template $tmpl_file --labels "delete=true" --properties $properties

# clean up file on disk
rm -f $tmpl_file
