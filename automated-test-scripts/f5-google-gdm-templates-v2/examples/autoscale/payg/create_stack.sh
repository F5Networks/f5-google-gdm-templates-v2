#  expectValue = "completed successfully"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0


# set vars
config_file='/tmp/examples/autoscale/<LICENSE TYPE>/<DEWPOINT JOB ID>-config.yaml'
runtime_file='<RUNTIME INIT>'
runtime_update_file='<RUNTIME INIT UPDATE>'

## Create runtime config with yq
cp -r $PWD/examples /tmp
cp /tmp/examples/autoscale/bigip-configurations/runtime-init-conf-<LICENSE TYPE>.yaml $runtime_file

/usr/bin/yq e ".extension_services.service_operations.[0].value.Common.admin.class = \"User\"" -i $runtime_file
/usr/bin/yq e ".extension_services.service_operations.[0].value.Common.admin.password = \"<SECRET VALUE>\"" -i $runtime_file
/usr/bin/yq e ".extension_services.service_operations.[0].value.Common.admin.shell = \"bash\"" -i $runtime_file
/usr/bin/yq e ".extension_services.service_operations.[0].value.Common.admin.userType = \"regular\"" -i $runtime_file
/usr/bin/yq e ".extension_services.service_operations.[1].value.Tenant_1.HTTPS_Service.WAFPolicy.enforcementMode = \"blocking\"" -i $runtime_file
/usr/bin/yq e ".extension_services.service_operations.[1].value.Tenant_1.HTTP_Service.WAFPolicy.enforcementMode = \"blocking\"" -i $runtime_file
/usr/bin/yq e ".extension_services.service_operations.[1].value.Tenant_1.HTTPS_Service.WAFPolicy.url = \"https://cdn.f5.com/product/cloudsolutions/solution-scripts/Rapid_Deployment_Policy_13_1.xml\"" -i $runtime_file
/usr/bin/yq e ".extension_services.service_operations.[1].value.Tenant_1.HTTP_Service.WAFPolicy.url = \"https://cdn.f5.com/product/cloudsolutions/solution-scripts/Rapid_Deployment_Policy_13_1.xml\"" -i $runtime_file

# Delete TS configuration
# References a Splunk that does not exist
/usr/bin/yq e "del(.runtime_parameters.[3])" -i $runtime_file
/usr/bin/yq e "del(.extension_services.service_operations.[2])" -i $runtime_file

cp $runtime_file $runtime_update_file
/usr/bin/yq e ".extension_services.service_operations.[1].value.Tenant_1.HTTPS_Service.WAFPolicy.enforcementMode = \"transparent\"" -i $runtime_update_file
/usr/bin/yq e ".extension_services.service_operations.[1].value.Tenant_1.HTTP_Service.WAFPolicy.enforcementMode = \"transparent\"" -i $runtime_update_file

# Print runtime config file
cat $runtime_file

# Upload runtime configs to container
config_result=$(gsutil cp $runtime_file gs://<STACK NAME>-bucket && gsutil acl ch -u AllUsers:R gs://<STACK NAME>-bucket/<DEWPOINT JOB ID>-runtime.yaml)
config_update_result=$(gsutil cp $runtime_update_file gs://<STACK NAME>-bucket && gsutil acl ch -u AllUsers:R gs://<STACK NAME>-bucket/update_<DEWPOINT JOB ID>-runtime.yaml)
config_url='https://storage.googleapis.com/<STACK NAME>-bucket/<DEWPOINT JOB ID>-runtime.yaml'
config_update_url='https://storage.googleapis.com/<STACK NAME>-bucket/update_<DEWPOINT JOB ID>-runtime.yaml'

## Run GDM Autoscale template
/usr/bin/yq e -n ".imports[0].path = \"autoscale.py\"" > $config_file
/usr/bin/yq e ".imports[1].path = \"../../modules/access/access.py\"" -i $config_file
/usr/bin/yq e ".imports[2].path = \"../../modules/application/application.py\"" -i $config_file
/usr/bin/yq e ".imports[3].path = \"../../modules/bigip-autoscale/bigip_autoscale.py\"" -i $config_file
/usr/bin/yq e ".imports[4].path = \"../../modules/dag/dag.py\"" -i $config_file
/usr/bin/yq e ".imports[5].path = \"../../modules/network/network.py\"" -i $config_file

/usr/bin/yq e ".resources[0].name = \"autoscale-py\"" -i $config_file
/usr/bin/yq e ".resources[0].type = \"autoscale.py\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.application = \"f5app\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.cost = \"f5cost\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.group = \"f5group\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.owner = \"f5owner\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.appContainerName = \"<APP CONTAINER NAME>\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.availabilityZone = \"<AVAILABILITY ZONE>\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.bigIpRuntimeInitPackageUrl = \"<BIGIP RUNTIME INIT PACKAGEURL>\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.bigIpRuntimeInitConfig = \"${config_url}\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.cooldownPeriodSec = <SCALING COOL DOWN PERIOD>" -i $config_file
/usr/bin/yq e ".resources[0].properties.imageName = \"<IMAGE NAME>\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.instanceTemplateVersion = <INSTANCE TEMPLATE VERSION>" -i $config_file
/usr/bin/yq e ".resources[0].properties.instanceType = \"<INSTANCE TYPE>\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.maxNumReplicas = <SCALING MAX>" -i $config_file
/usr/bin/yq e ".resources[0].properties.minNumReplicas = <SCALING MIN>" -i $config_file
/usr/bin/yq e ".resources[0].properties.provisionPublicIp = <PROVISION PUBLIC IP>" -i $config_file
/usr/bin/yq e ".resources[0].properties.region = \"<REGION>\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.restrictedSrcAddressMgmt = \"<RESTRICTED SRC ADDRESS>\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.restrictedSrcAddressApp = \"<RESTRICTED SRC ADDRESS APP>\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.restrictedSrcAddressAppInternal = \"<RESTRICTED SRC ADDRESS APP INTERNAL>\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.uniqueString = \"<UNIQUESTRING>\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.update = False" -i $config_file
/usr/bin/yq e ".resources[0].properties.utilizationTarget = <SCALING UTILIZATION TARGET>" -i $config_file

# print out config file
/usr/bin/yq e $config_file

labels="delete=true"

gcloud="gcloud deployment-manager deployments create <STACK NAME> --labels $labels --config $config_file"
$gcloud
