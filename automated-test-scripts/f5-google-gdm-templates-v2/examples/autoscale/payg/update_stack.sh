#  expectValue = "completed with warnings"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0


# set vars
config_file='/tmp/examples/autoscale/<LICENSE TYPE>/update_<DEWPOINT JOB ID>-config.yaml'

# Updated runtime init config from create_stack.sh
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
/usr/bin/yq e ".resources[0].properties.zone = \"<AVAILABILITY ZONE>\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.bigIpRuntimeInitPackageUrl = \"<BIGIP RUNTIME INIT PACKAGEURL>\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.bigIpRuntimeInitConfig = \"${config_update_url}\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.bigIpScalingMinSize = <SCALING MIN>" -i $config_file
/usr/bin/yq e ".resources[0].properties.bigIpScalingMaxSize = <SCALING MAX>" -i $config_file
/usr/bin/yq e ".resources[0].properties.bigIpScaleOutCpuThreshold = <SCALING UTILIZATION TARGET>" -i $config_file
/usr/bin/yq e ".resources[0].properties.bigIpCoolDownPeriodSec = <SCALING COOL DOWN PERIOD>" -i $config_file
/usr/bin/yq e ".resources[0].properties.bigIpImageName = \"<IMAGE NAME>\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.bigIpInstanceTemplateVersion = <INSTANCE TEMPLATE VERSION UPDATE>" -i $config_file
/usr/bin/yq e ".resources[0].properties.bigIpInstanceType = \"<INSTANCE TYPE>\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.provisionPublicIp = <PROVISION PUBLIC IP>" -i $config_file
/usr/bin/yq e ".resources[0].properties.region = \"<REGION>\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.restrictedSrcAddressMgmt[0] = \"<RESTRICTED SRC ADDRESS>\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.restrictedSrcAddressApp[0] = \"<RESTRICTED SRC ADDRESS APP>\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.uniqueString = \"<UNIQUESTRING>\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.update = True" -i $config_file

# print out config file
/usr/bin/yq e $config_file

gcloud="gcloud deployment-manager deployments update <STACK NAME> --config $config_file"
$gcloud
