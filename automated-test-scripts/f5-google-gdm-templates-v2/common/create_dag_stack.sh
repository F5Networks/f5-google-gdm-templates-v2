#  expectValue = "completed successfully"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0


# set vars
TMP_DIR="/tmp/<DEWPOINT JOB ID>"
tmpl_file='/tmp/dag.py'

# grab template and schema
curl -k <DAG TEMPLATE URL> -o $tmpl_file
curl -k <DAG TEMPLATE URL>.schema -o "${tmpl_file}.schema"

# source test functions
source ${TMP_DIR}/test_functions.sh

# determine test environment public ip address
source_cidr=$(get_env_public_ip)
echo "source_cidr=$source_cidr"

mgmtNetworkSelfLink=''
mgmtSubnetSelfLink=''
externalNetworkSelfLink=''
externalSubnetSelfLink=''
internalNetworkSelfLink=''
internalSubnetSelfLink=''
appNetworkSelfLink=''
appSubnetSelfLink=''
instances=''
instanceGroupSelfLink=''

if [ <NUMBER NICS> -lt 2 ]; then
    mgmtNetworkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<UNIQUESTRING>-network0-network" '.[] | select(.name | contains($n)) | .selfLink')
    mgmtSubnetSelfLink=$(gcloud compute networks subnets list --format json | jq -r --arg n "<UNIQUESTRING>-subnet0-subnet" '.[] | select(.name | contains($n)) | .selfLink')

    appNetworkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<UNIQUESTRING>-network1-network" '.[] | select(.name | contains($n)) | .selfLink')
    appSubnetSelfLink=$(gcloud compute networks subnets list --format json | jq -r --arg n "<UNIQUESTRING>-subnet1-subnet" '.[] | select(.name | contains($n)) | .selfLink')
fi


if [ <NUMBER NICS> -ge 2 ]; then
    mgmtNetworkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<UNIQUESTRING>-network1-network" '.[] | select(.name | contains($n)) | .selfLink')
    mgmtSubnetSelfLink=$(gcloud compute networks subnets list --format json | jq -r --arg n "<UNIQUESTRING>-subnet1-subnet" '.[] | select(.name | contains($n)) | .selfLink')

    appNetworkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<UNIQUESTRING>-network0-network" '.[] | select(.name | contains($n)) | .selfLink')
    appSubnetSelfLink=$(gcloud compute networks subnets list --format json | jq -r --arg n "<UNIQUESTRING>-subnet0-subnet" '.[] | select(.name | contains($n)) | .selfLink')

    externalNetworkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<UNIQUESTRING>-network2-network" '.[] | select(.name | contains($n)) | .selfLink')
    externalSubnetSelfLink=$(gcloud compute networks subnets list --format json | jq -r --arg n "<UNIQUESTRING>-subnet2-subnet" '.[] | select(.name | contains($n)) | .selfLink')
fi

if [ <NUMBER NICS> -ge 3 ]; then
    internalNetworkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<UNIQUESTRING>-network3-network" '.[] | select(.name | contains($n)) | .selfLink')
    internalSubnetSelfLink=$(gcloud compute networks subnets list --format json | jq -r --arg n "<UNIQUESTRING>-subnet3-subnet" '.[] | select(.name | contains($n)) | .selfLink')
fi

if [ <NUMBER NICS> -eq 1 ]; then
    internalNetworkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<UNIQUESTRING>-network0-network" '.[] | select(.name | contains($n)) | .selfLink')
    internalSubnetSelfLink=$(gcloud compute networks subnets list --format json | jq -r --arg n "<UNIQUESTRING>-subnet0-subnet" '.[] | select(.name | contains($n)) | .selfLink')
fi

if [ "<TEMPLATE NAME>" == "dag.py" && <AUTOSCALE> ]; then
    # instances used by the external forwarding rule/target pool
    instances=()
    response=$(gcloud compute instance-groups list-instances <UNIQUESTRING>-bigip-ig --region <REGION> --format=json | jq -r .[].instance)
    for item in $response
    do
        instances+=($(echo ${item}))
    done

    # instances used by the internal forwarding rule/backend service
    instanceGroupSelfLink=$(gcloud compute instance-groups describe <UNIQUESTRING>-bigip-igm --region <REGION> --format=json | jq -r .selfLink)
fi
if [ "<AUTOSCALE>" == "True" ]; then
    instanceGroupSelfLink=$(gcloud compute instance-groups describe <UNIQUESTRING>-bigip-igm --zone <AVAILABILITY ZONE> --format=json | jq -r .selfLink)
    targetGroupSelfLink=$(gcloud compute target-pools list --format=json | jq -r --arg n "<UNIQUESTRING>-bigip-tp" '.[] | select(.name | contains($n)) | .selfLink')
fi

# Run GDM Dag template
/usr/bin/yq e -n ".imports[0].path = \"${tmpl_file}\"" > <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].name = \"dag\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].type = \"dag.py\"" -i <DEWPOINT JOB ID>.yaml

/usr/bin/yq e ".resources[0].properties.uniqueString = \"<UNIQUESTRING>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.update = True" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.region = \"<REGION>\"" -i <DEWPOINT JOB ID>.yaml

/usr/bin/yq e ".resources[0].properties.guiPortMgmt = <MGMT PORT>" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.applicationVipPort = \"<APP PORT>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.applicationPort = \"<APP INTERNAL PORT>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.restrictedSrcAddressMgmt = \"${source_cidr}\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.restrictedSrcAddressApp = \"${source_cidr}\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.restrictedSrcAddressAppInternal = \"${source_cidr}\"" -i <DEWPOINT JOB ID>.yaml

/usr/bin/yq e ".resources[0].properties.numberOfNics = <NUMBER NICS>" -i <DEWPOINT JOB ID>.yaml

/usr/bin/yq e ".resources[0].properties.networkSelfLinkMgmt = \"$mgmtNetworkSelfLink\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.subnetSelfLinkMgmt = \"$mgmtSubnetSelfLink\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.networkSelfLinkApp = \"$appNetworkSelfLink\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.subnetSelfLinkApp = \"$appSubnetSelfLink\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.networkSelfLinkExternal = \"$externalNetworkSelfLink\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.subnetSelfLinkExternal = \"$externalSubnetSelfLink\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.networkSelfLinkInternal = \"$internalNetworkSelfLink\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.subnetSelfLinkInternal = \"$internalSubnetSelfLink\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.numberOfForwardingRules = <NUM FORWARDING RULES>" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.numberOfInternalForwardingRules = <NUM INTERNAL FORWARDING RULES>" -i <DEWPOINT JOB ID>.yaml

if [ "<AUTOSCALE>" == "True" ]; then
    /usr/bin/yq e ".resources[0].properties.instanceGroups[0] = \"$instanceGroupSelfLink\"" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[0].properties.targetPoolSelfLink = \"$targetGroupSelfLink\"" -i <DEWPOINT JOB ID>.yaml
fi
# print out config file
/usr/bin/yq e <DEWPOINT JOB ID>.yaml

labels="delete=true"

gcloud="gcloud deployment-manager deployments create <DAG STACK NAME> --labels $labels --config <DEWPOINT JOB ID>.yaml"
$gcloud
