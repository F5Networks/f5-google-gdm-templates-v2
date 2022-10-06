#  expectValue = "completed successfully"
#  expectFailValue = "Failed"
#  scriptTimeout = 15
#  replayEnabled = false
#  replayTimeout = 0


# set vars
TMP_DIR='/tmp/<DEWPOINT JOB ID>'
if [[ "<PROVISION PUBLIC IP>" == "False" ]]; then
    src_ip_mgmt=$(gcloud compute networks subnets list --format json | jq -r --arg n "<UNIQUESTRING>-mgmt-subnet" '.[] | select(.name | contains($n)) | .ipCidrRange')
else
    src_ip_mgmt=$(curl ifconfig.me)/32
fi
config_file='/tmp/examples/autoscale/<LICENSE TYPE>/<DEWPOINT JOB ID>-config.yaml'
runtime_file='<RUNTIME INIT>'
runtime_update_file='<RUNTIME INIT UPDATE>'
mkdir -p /tmp/examples/autoscale/<LICENSE TYPE>

LICENSE_HOST=''
if [[ "<LICENSE TYPE>" == "bigiq" ]]; then
    if [ -f "${TMP_DIR}/bigiq_info.json" ]; then
        echo "Found existing BIG-IQ"
        cat ${TMP_DIR}/bigiq_info.json
        bigiq_address=$(cat ${TMP_DIR}/bigiq_info.json | jq -r .bigiq_address)
        bigiq_password=$(cat ${TMP_DIR}/bigiq_info.json | jq -r .bigiq_password)
    else
        echo "Failed - No BIG-IQ found"
    fi
    LICENSE_HOST=$bigiq_address
fi

## Create runtime config with yq
cp -r $PWD/examples /tmp
cp /tmp/examples/autoscale/bigip-configurations/runtime-init-conf-<LICENSE TYPE>-with-app.yaml $runtime_file

# Uncomment to debug
/usr/bin/yq e ".controls.logLevel = \"silly\"" -i $runtime_file

/usr/bin/yq e ".extension_services.service_operations.[0].value.Common.admin.class = \"User\"" -i $runtime_file
/usr/bin/yq e ".extension_services.service_operations.[0].value.Common.admin.password = \"<SECRET VALUE>\"" -i $runtime_file
/usr/bin/yq e ".extension_services.service_operations.[0].value.Common.admin.shell = \"bash\"" -i $runtime_file
/usr/bin/yq e ".extension_services.service_operations.[0].value.Common.admin.userType = \"regular\"" -i $runtime_file

/usr/bin/yq e ".extension_services.service_operations.[1].value.Tenant_1.Shared.Custom_WAF_Policy.enforcementMode = \"blocking\"" -i $runtime_file
/usr/bin/yq e ".extension_services.service_operations.[1].value.Tenant_1.Shared.Custom_WAF_Policy.url = \"https://cdn.f5.com/product/cloudsolutions/solution-scripts/Rapid_Deployment_Policy_13_1.xml\"" -i $runtime_file

if [[ "<LICENSE TYPE>" == "bigiq" ]]; then
    /usr/bin/yq e ".extension_services.service_operations.[0].value.Common.My_License.licensePool = \"production\"" -i $runtime_file
    /usr/bin/yq e ".extension_services.service_operations.[0].value.Common.My_License.bigIqHost = \"${LICENSE_HOST}\"" -i $runtime_file
    /usr/bin/yq e ".extension_services.service_operations.[0].value.Common.My_License.tenant = \"<DEWPOINT JOB ID>-{{{INSTANCE_ID}}}\"" -i $runtime_file
fi

cp $runtime_file $runtime_update_file
/usr/bin/yq e ".extension_services.service_operations.[1].value.Tenant_1.Shared.Custom_WAF_Policy.enforcementMode = \"transparent\"" -i $runtime_update_file

# Print runtime config file
cat $runtime_file

# Upload runtime configs to container
config_result=$(gsutil cp $runtime_file gs://<STACK NAME>-bucket && gsutil acl ch -u AllUsers:R gs://<STACK NAME>-bucket/<DEWPOINT JOB ID>-runtime.yaml)
config_update_result=$(gsutil cp $runtime_update_file gs://<STACK NAME>-bucket && gsutil acl ch -u AllUsers:R gs://<STACK NAME>-bucket/update_<DEWPOINT JOB ID>-runtime.yaml)
config_url='https://storage.googleapis.com/<STACK NAME>-bucket/<DEWPOINT JOB ID>-runtime.yaml'
config_update_url='https://storage.googleapis.com/<STACK NAME>-bucket/update_<DEWPOINT JOB ID>-runtime.yaml'

## Run GDM Autoscale template
/usr/bin/yq e -n ".imports[0].path = \"autoscale-existing-network.py\"" > $config_file
/usr/bin/yq e ".imports[1].path = \"../../modules/access/access.py\"" -i $config_file
/usr/bin/yq e ".imports[2].path = \"../../modules/application/application.py\"" -i $config_file
/usr/bin/yq e ".imports[3].path = \"../../modules/bigip-autoscale/bigip_autoscale.py\"" -i $config_file
/usr/bin/yq e ".imports[4].path = \"../../modules/dag/dag.py\"" -i $config_file
/usr/bin/yq e ".imports[5].path = \"../../modules/function/function.py\"" -i $config_file

/usr/bin/yq e ".resources[0].name = \"autoscale-existing-network-py\"" -i $config_file
/usr/bin/yq e ".resources[0].type = \"autoscale-existing-network.py\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.allowUsageAnalytics = False" -i $config_file
/usr/bin/yq e ".resources[0].properties.application = \"f5app\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.cost = \"f5cost\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.environment = \"f5env\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.group = \"f5group\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.owner = \"f5owner\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.zones[0] = \"<AVAILABILITY ZONE 1>\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.zones[1] = \"<AVAILABILITY ZONE 2>\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.bigIpCustomImageId = \"<CUSTOM IMAGE ID>\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.bigIpRuntimeInitConfig = \"${config_url}\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.bigIpScalingMinSize = <SCALING MIN>" -i $config_file
/usr/bin/yq e ".resources[0].properties.bigIpScalingMaxSize = <SCALING MAX>" -i $config_file
/usr/bin/yq e ".resources[0].properties.bigIpScaleOutCpuThreshold = <SCALING UTILIZATION TARGET>" -i $config_file
/usr/bin/yq e ".resources[0].properties.bigIpCoolDownPeriodSec = <SCALING COOL DOWN PERIOD>" -i $config_file
/usr/bin/yq e ".resources[0].properties.bigIpImageName = \"<IMAGE NAME>\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.bigIpInstanceTemplateVersion = <INSTANCE TEMPLATE VERSION>" -i $config_file
/usr/bin/yq e ".resources[0].properties.bigIpInstanceType = \"<INSTANCE TYPE>\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.bigIqSecretId = \"<STACK NAME>-secret\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.logId = \"<LOG ID>\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.provisionPublicIp = <PROVISION PUBLIC IP>" -i $config_file
/usr/bin/yq e ".resources[0].properties.networkName = \"<UNIQUESTRING>-network-network\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.subnets.mgmtSubnetName = \"<UNIQUESTRING>-mgmt-subnet\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.subnets.appSubnetName = \"<UNIQUESTRING>-app-subnet\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.region = \"<REGION>\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.restrictedSrcAddressMgmt[0] = \"${src_ip_mgmt}\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.uniqueString = \"<UNIQUESTRING>\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.update = False" -i $config_file

# print out config file
/usr/bin/yq e $config_file

labels="delete=true"

gcloud="gcloud deployment-manager deployments create <STACK NAME>-bigiq --labels $labels --config $config_file"
$gcloud