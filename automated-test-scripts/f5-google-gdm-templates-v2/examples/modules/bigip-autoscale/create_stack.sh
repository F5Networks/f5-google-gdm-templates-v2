#  expectValue = "completed successfully"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0

# set vars
TMP_DIR="/tmp/<DEWPOINT JOB ID>"
tmpl_file='/tmp/bigip_autoscale.py'
instance_tmpl_file='/tmp/bigip_instance_template.py'

# grab template and schema
curl -k <TEMPLATE URL> -o $tmpl_file
curl -k <TEMPLATE URL>.schema -o "${tmpl_file}.schema"
curl -k <INSTANCE TEMPLATE URL> -o $instance_tmpl_file

# source test functions
source ${TMP_DIR}/test_functions.sh

networkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<DEWPOINT JOB ID>-network0" '.[] | select(.name | contains($n)) | .selfLink')
subnetSelfLink=$(gcloud compute networks subnets list --format json | jq -r --arg n "<DEWPOINT JOB ID>-subnet0" '.[] | select(.name | contains($n)) | .selfLink')

# Run GDM Dag template
/usr/bin/yq e -n ".imports[0].path = \"${tmpl_file}\"" > <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".imports[1].path = \"${instance_tmpl_file}\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].name = \"bigip-autoscale-py\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].type = \"bigip_autoscale.py\"" -i <DEWPOINT JOB ID>.yaml

/usr/bin/yq e ".resources[0].properties.serviceAccountEmail = \"<SERVICE ACCOUNT EMAIL>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.project = \"<PROJECT>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.minNumReplicas = <SCALING MIN>" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.maxNumReplicas = <SCALING MAX>" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.utilizationTarget = <SCALING UTILIZATION TARGET>" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.coolDownPeriodSec = <SCALING COOL DOWN PERIOD>" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.region = \"<REGION>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.applicationVipPort = <APP PORT>" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.availabilityZone = \"<AVAILABILITY ZONE>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.imageName = \"<IMAGE NAME>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.bigIpRuntimeInitConfig = \"<BIGIP RUNTIME INIT CONFIG>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.bigIpRuntimeInitPackageUrl = \"<BIGIP RUNTIME INIT PACKAGEURL>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.hostname = \"<HOST NAME>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.instanceType = \"<INSTANCE TYPE>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.instanceTemplateVersion = 1" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.uniqueString = \"<UNIQUESTRING>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.networkSelfLink = \"$networkSelfLink\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.subnetSelfLink = \"$subnetSelfLink\"" -i <DEWPOINT JOB ID>.yaml

# print out config file
/usr/bin/yq e <DEWPOINT JOB ID>.yaml

labels="delete=true"

gcloud="gcloud deployment-manager deployments create <STACK NAME> --labels $labels --config <DEWPOINT JOB ID>.yaml"
$gcloud
