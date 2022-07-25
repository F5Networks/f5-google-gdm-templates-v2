#  expectValue = "completed successfully"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0


# set vars
if [[ "<PROVISION PUBLIC IP>" == "False" ]]; then
    src_ip=$(gcloud compute networks subnets list --format json | jq -r --arg n "<UNIQUESTRING>-mgmt-subnet" '.[] | select(.name | contains($n)) | .ipCidrRange')
else
    src_ip=$(curl ifconfig.me)/32
fi

curl -L https://github.com/F5Networks/f5-google-gdm-templates-v2/archive/main.tar.gz -o main.tar.gz && tar -xvf main.tar.gz
config_file='f5-google-gdm-templates-v2-main/examples/autoscale/payg/<DEWPOINT JOB ID>.yaml'
cp f5-google-gdm-templates-v2-main/examples/autoscale/payg/sample_autoscale_existing_network.yaml $config_file

## Run GDM Autoscale template
/usr/bin/yq e ".imports[0].path = \"autoscale-existing-network.py\"" -i $config_file

/usr/bin/yq e ".resources[0].name = \"autoscale-existing-network-py\"" -i $config_file
/usr/bin/yq e ".resources[0].type = \"<TEMPLATE NAME>\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.networkName = \"<UNIQUESTRING>-network-network\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.subnets.mgmtSubnetName = \"<UNIQUESTRING>-mgmt-subnet\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.subnets.appSubnetName = \"<UNIQUESTRING>-app-subnet\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.region = \"<REGION>\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.restrictedSrcAddressMgmt[0] = \"${src_ip}\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.restrictedSrcAddressApp[0] = \"${src_ip}\"" -i $config_file
/usr/bin/yq e ".resources[0].properties.uniqueString = \"<UNIQUESTRING>\"" -i $config_file

# print out config file
/usr/bin/yq e $config_file

labels="delete=true"

gcloud="gcloud deployment-manager deployments create <STACK NAME> --labels $labels --config $config_file"
$gcloud
