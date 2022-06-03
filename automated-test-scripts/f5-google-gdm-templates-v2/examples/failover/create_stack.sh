#  expectValue = "completed successfully"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0

src_ip=$(curl ifconfig.me)/32
tmpl_path="/tmp/examples/failover/"

# grab template and schema
cp -r $PWD/examples /tmp

# Run GDM failover template
cp /tmp/examples/failover/sample_failover.yaml ${tmpl_path}<DEWPOINT JOB ID>.yaml
# Update Config File using sample_failover.yaml 
/usr/bin/yq e ".resources[0].name = \"failover-py\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.restrictedSrcAddressApp[0] = \"${src_ip}\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.restrictedSrcAddressMgmt[0] = \"${src_ip}\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.bigIpRuntimeInitConfig01 = \"<BIGIP RUNTIME INIT CONFIG>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.bigIpRuntimeInitConfig02 = \"<BIGIP RUNTIME INIT CONFIG 2>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.bigIpImageName = \"<IMAGE NAME>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.bigIpInstanceType = \"<INSTANCE TYPE>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.cfeTag = \"<DEWPOINT JOB ID>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.provisionPublicIp = <PROVISION PUBLIC IP>" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.region = \"<REGION>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.uniqueString = \"<UNIQUESTRING>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.zone = \"<AVAILABILITY ZONE>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].type = \"<TEMPLATE NAME>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml

# print out config file
/usr/bin/yq e ${tmpl_path}<DEWPOINT JOB ID>.yaml
labels="delete=true"
gcloud="gcloud deployment-manager deployments create <STACK NAME> --labels $labels --config ${tmpl_path}<DEWPOINT JOB ID>.yaml"
$gcloud
