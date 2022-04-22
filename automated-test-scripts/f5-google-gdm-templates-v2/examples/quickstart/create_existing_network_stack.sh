#  expectValue = "completed successfully"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0

tmpl_path="/tmp/examples/quickstart/"

src_ip_app=$(curl ifconfig.me)/32
src_ip_mgmt=$src_ip_app
if [[ "<PROVISION PUBLIC IP>" == "False" ]]; then
    src_ip_mgmt=$(gcloud compute networks subnets list --format json | jq -r --arg n "<UNIQUESTRING>-subnet0-subnet" '.[] | select(.name | contains($n)) | .ipCidrRange')
fi

# grab template and schema
cp -r $PWD/examples /tmp

# Run GDM quickstart template
cp /tmp/examples/quickstart/sample_quickstart_existing_network.yaml ${tmpl_path}<DEWPOINT JOB ID>.yaml
# Update Config File using sample_quickstart_existing_network.yaml
/usr/bin/yq e ".resources[0].name = \"quickstart-existing-network-py\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.restrictedSrcAddressApp[0] = \"${src_ip_app}\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.restrictedSrcAddressMgmt[0] = \"${src_ip_mgmt}\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.bigIpRuntimeInitConfig = \"<BIGIP RUNTIME INIT CONFIG>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.bigIpRuntimeInitPackageUrl = \"<BIGIP RUNTIME INIT PACKAGEURL>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.bigIpImageName = \"<IMAGE NAME>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.bigIpInstanceType = \"<INSTANCE TYPE>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.numNics = <NUMBER NICS>" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.provisionPublicIp = <PROVISION PUBLIC IP>" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.networks.externalNetworkName = \"<UNIQUESTRING>-network1-network\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.networks.internalNetworkName = \"<UNIQUESTRING>-network2-network\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.networks.mgmtNetworkName = \"<UNIQUESTRING>-network0-network\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.subnets.mgmtSubnetName = \"<UNIQUESTRING>-subnet0-subnet\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.subnets.appSubnetName = \"<UNIQUESTRING>-subnet1-subnet\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.subnets.internalSubnetName = \"<UNIQUESTRING>-subnet2-subnet\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.region = \"<REGION>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.uniqueString = \"<UNIQUESTRING>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.zone = \"<AVAILABILITY ZONE>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].type = \"<TEMPLATE NAME>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml

# print out config file
/usr/bin/yq e ${tmpl_path}<DEWPOINT JOB ID>.yaml
labels="delete=true"
gcloud="gcloud deployment-manager deployments create <STACK NAME> --labels $labels --config ${tmpl_path}<DEWPOINT JOB ID>.yaml"
$gcloud
