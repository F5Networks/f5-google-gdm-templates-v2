#  expectValue = "completed successfully"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0

# set vars
TMP_DIR="/tmp/<DEWPOINT JOB ID>"
tmpl_file='/tmp/application.py'
instance_tmpl_file='/tmp/application_instance_template.py'

# grab template and schema
curl -k <TEMPLATE URL> -o $tmpl_file
curl -k <TEMPLATE URL>.schema -o "${tmpl_file}.schema"
curl -k <INSTANCE TEMPLATE URL> -o $instance_tmpl_file

# source test functions
source ${TMP_DIR}/test_functions.sh

networkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<DEWPOINT JOB ID>-network1" '.[] | select(.name | contains($n)) | .selfLink')
subnetSelfLink=$(gcloud compute networks subnets list --format json | jq -r --arg n "<DEWPOINT JOB ID>-subnet1" '.[] | select(.name | contains($n)) | .selfLink')

# Run GDM Dag template
/usr/bin/yq e -n ".imports[0].path = \"${tmpl_file}\"" > <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".imports[1].path = \"${instance_tmpl_file}\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].name = \"application\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].type = \"application.py\"" -i <DEWPOINT JOB ID>.yaml

/usr/bin/yq e ".resources[0].properties.appContainerName = \"<APP CONTAINER NAME>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.createAutoscaleGroup = <AUTOSCALE>" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.availabilityZone = \"<AVAILABILITY ZONE>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.hostname = \"<HOST NAME>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.instanceTemplateVersion = 1" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.instanceType = \"<INSTANCE TYPE>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.uniqueString = \"<UNIQUESTRING>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.networkSelfLink = \"$networkSelfLink\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.subnetSelfLink = \"$subnetSelfLink\"" -i <DEWPOINT JOB ID>.yaml

# print out config file
/usr/bin/yq e <DEWPOINT JOB ID>.yaml

labels="delete=true"

gcloud="gcloud deployment-manager deployments create <STACK NAME> --labels $labels --config <DEWPOINT JOB ID>.yaml"
$gcloud
