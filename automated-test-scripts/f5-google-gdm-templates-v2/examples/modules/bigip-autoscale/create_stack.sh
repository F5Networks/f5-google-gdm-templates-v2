#  expectValue = "completed successfully"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0

# set vars
TMP_DIR="/tmp/<DEWPOINT JOB ID>"
tmpl_file='/tmp/bigip_autoscale.py'

# grab template and schema
curl -k <TEMPLATE URL> -o $tmpl_file
curl -k <TEMPLATE URL>.schema -o "${tmpl_file}.schema"

# source test functions
source ${TMP_DIR}/test_functions.sh

networkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<UNIQUESTRING>-network0-network" '.[] | select(.name | contains($n)) | .selfLink')
subnetSelfLink=$(gcloud compute networks subnets list --format json | jq -r --arg n "<UNIQUESTRING>-subnet0-subnet" '.[] | select(.name | contains($n)) | .selfLink')

# Run GDM Dag template
/usr/bin/yq e -n ".imports[0].path = \"${tmpl_file}\"" > <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].name = \"bigip-autoscale-py\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].type = \"bigip_autoscale.py\"" -i <DEWPOINT JOB ID>.yaml

/usr/bin/yq e ".resources[0].properties.application = \"f5app\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.cost = \"f5cost\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.group = \"f5group\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.owner = \"f5owner\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.serviceAccountEmail = \"<SERVICE ACCOUNT EMAIL>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.project = \"<PROJECT>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.autoscalers[0].autoscalingPolicy.minNumReplicas = <SCALING MIN>" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.autoscalers[0].autoscalingPolicy.maxNumReplicas = <SCALING MAX>" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.autoscalers[0].autoscalingPolicy.cpuUtilization.utilizationTarget = <SCALING UTILIZATION TARGET>" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.autoscalers[0].autoscalingPolicy.coolDownPeriodSec = <SCALING COOL DOWN PERIOD>" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.autoscalers[0].zone = \"<AVAILABILITY ZONE>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.autoscalers[0].name = \"bigip\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.region = \"<REGION>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.healthChecks[0].httpHealthCheck.port = <APP PORT>" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.healthChecks[0].httpHealthCheck.type = \"HTTP\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.healthChecks[0].name = \"<UNIQUESTRING>-external-hc\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.imageName = \"<IMAGE NAME>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.bigIpRuntimeInitConfig = \"<BIGIP RUNTIME INIT CONFIG>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.bigIpRuntimeInitPackageUrl = \"<BIGIP RUNTIME INIT PACKAGEURL>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.instanceGroupManagers[0].zone = \"<AVAILABILITY ZONE>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.instanceGroupManagers[0].name = \"bigip\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.instanceTemplates[0].hostname = \"<HOST NAME>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.instanceTemplates[0].name = \"bigip\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.instanceType = \"<INSTANCE TYPE>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.instanceTemplateVersion = 1" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.targetPools[0].region = \"<REGION>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.targetPools[0].name = \"bigip\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.uniqueString = \"<UNIQUESTRING>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.networkSelfLink = \"$networkSelfLink\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.subnetSelfLink = \"$subnetSelfLink\"" -i <DEWPOINT JOB ID>.yaml

# print out config file
/usr/bin/yq e <DEWPOINT JOB ID>.yaml

labels="delete=true"

gcloud="gcloud deployment-manager deployments create <STACK NAME> --labels $labels --config <DEWPOINT JOB ID>.yaml"
$gcloud
