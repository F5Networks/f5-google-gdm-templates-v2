#  expectValue = "completed successfully"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0

tmpl_path="/tmp/examples/failover/"

src_ip_app=$(curl ifconfig.me)/32
src_ip_mgmt=$src_ip_app
if [[ "<PROVISION PUBLIC IP>" == "False" ]]; then
    src_ip_mgmt=$(gcloud compute networks subnets list --format json | jq -r --arg n "<UNIQUESTRING>-subnet0-subnet" '.[] | select(.name | contains($n)) | .ipCidrRange')
fi

# Add lic key if byol
license_key_01=''
license_key_02=''
if [[ "<LICENSE TYPE>" == "byol" ]]; then
    license_key_01='<AUTOFILL EVAL LICENSE KEY>'
    license_key_02='<AUTOFILL EVAL LICENSE KEY 2>'
fi

# Add internal networking if doing 3nic
internal_network_name=''
internal_subnet_name=''
if [[ <NUMBER NICS> == 3 ]]; then
    internal_network_name='<UNIQUESTRING>-network2-network'
    internal_subnet_name='<UNIQUESTRING>-subnet2-subnet'
fi

# grab template and schema
cp -r $PWD/examples /tmp

# Run GDM failover template
cp /tmp/examples/failover/sample_failover_existing_network.yaml ${tmpl_path}<DEWPOINT JOB ID>.yaml
# Update Config File using sample_failover_existing_network.yaml
/usr/bin/yq e ".resources[0].name = \"failover-existing-network-py\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.allowUsageAnalytics = False" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.numNics = <NUMBER NICS>" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.restrictedSrcAddressApp[0] = \"${src_ip_app}\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.restrictedSrcAddressMgmt[0] = \"${src_ip_mgmt}\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.bigIpCustomImageId = \"<CUSTOM IMAGE ID>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.bigIpLicenseKey01 = \"${license_key_01}\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.bigIpLicenseKey02 = \"${license_key_02}\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.bigIpRuntimeInitConfig01 = \"<BIGIP RUNTIME INIT CONFIG>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.bigIpRuntimeInitConfig02 = \"<BIGIP RUNTIME INIT CONFIG 2>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.bigIpImageName = \"<IMAGE NAME>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.bigIpInstanceType = \"<INSTANCE TYPE>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.bigIpSecretId = \"<STACK NAME>-secret\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.bigIpServiceAccountEmail = \"<UNIQUESTRING>-admin@f5-7656-pdsoleng-dev.iam.gserviceaccount.com\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.cfeTag = \"<DEWPOINT JOB ID>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.provisionPublicIp = <PROVISION PUBLIC IP>" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.networks.externalNetworkName = \"<UNIQUESTRING>-network1-network\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.networks.internalNetworkName = \"${internal_network_name}\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.networks.mgmtNetworkName = \"<UNIQUESTRING>-network0-network\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.subnets.mgmtSubnetName = \"<UNIQUESTRING>-subnet0-subnet\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.subnets.externalSubnetName = \"<UNIQUESTRING>-subnet1-subnet\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.subnets.internalSubnetName = \"${internal_subnet_name}\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.region = \"<REGION>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.uniqueString = \"<UNIQUESTRING>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.zones[0] = \"<AVAILABILITY ZONE BIGIP 1>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.zones[1] = \"<AVAILABILITY ZONE BIGIP 2>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].type = \"<TEMPLATE NAME>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml

# print out config file
/usr/bin/yq e ${tmpl_path}<DEWPOINT JOB ID>.yaml
labels="delete=true"
gcloud="gcloud deployment-manager deployments create <STACK NAME> --labels $labels --config ${tmpl_path}<DEWPOINT JOB ID>.yaml"
$gcloud
