#  expectValue = "completed successfully"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0

# set vars
TMP_DIR="/tmp/<DEWPOINT JOB ID>"
tmpl_file='/tmp/bastion.py'

# grab template and schema
curl -k <TEMPLATE URL> -o $tmpl_file
curl -k <TEMPLATE URL>.schema -o "${tmpl_file}.schema"

# source test functions
source ${TMP_DIR}/test_functions.sh

networkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<UNIQUESTRING>-network1-network" '.[] | select(.name | contains($n)) | .selfLink')
subnetSelfLink=$(gcloud compute networks subnets list --format json | jq -r --arg n "<UNIQUESTRING>-subnet1-subnet" '.[] | select(.name | contains($n)) | .selfLink')

# Run GDM Dag template
/usr/bin/yq e -n ".imports[0].path = \"${tmpl_file}\"" > <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].name = \"bastion\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].type = \"bastion.py\"" -i <DEWPOINT JOB ID>.yaml

/usr/bin/yq e ".resources[0].properties.osImage = \"<OS IMAGE>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.createAutoscaleGroup = <AUTOSCALE>" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.availabilityZone = \"<AVAILABILITY ZONE>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.hostname = \"<HOST NAME>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.instanceTemplateVersion = 1" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.instanceType = \"<INSTANCE TYPE>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.uniqueString = \"<UNIQUESTRING>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.networkSelfLink = \"$networkSelfLink\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.subnetSelfLink = \"$subnetSelfLink\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.application = \"f5app\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.cost = \"f5cost\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.group = \"f5group\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.owner = \"f5owner\"" -i <DEWPOINT JOB ID>.yaml

# print out config file
/usr/bin/yq e <DEWPOINT JOB ID>.yaml

labels="delete=true"

gcloud="gcloud deployment-manager deployments create <STACK NAME> --labels $labels --config <DEWPOINT JOB ID>.yaml"
$gcloud
