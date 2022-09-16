#  expectValue = "completed successfully"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0


src_ip=$(curl ifconfig.me)/32
if [[ "<PROVISION PUBLIC IP>" == "False" ]]; then
    src_ip=$(gcloud compute networks subnets list --format json | jq -r --arg n "<UNIQUESTRING>-subnet0-subnet" '.[] | select(.name | contains($n)) | .ipCidrRange')
fi

# grab template and schema
curl -L https://github.com/F5Networks/f5-google-gdm-templates-v2/archive/main.tar.gz -o main.tar.gz && tar -xvf main.tar.gz
config_file='f5-google-gdm-templates-v2-main/examples/quickstart/<DEWPOINT JOB ID>.yaml'

if echo "<TEMPLATE URL>" | grep -q "existing-network"; then
    echo "Using existing network"

    # Run GDM quickstart template
    cp f5-google-gdm-templates-v2-main/examples/quickstart/sample_quickstart_existing_network.yaml $config_file

    # Update Config File using sample_quickstart_existing_network.yaml
    /usr/bin/yq e ".resources[0].name = \"quickstart-existing-network-py\"" -i $config_file
    /usr/bin/yq e ".resources[0].properties.allowUsageAnalytics = False" -i $config_file
    /usr/bin/yq e ".resources[0].properties.restrictedSrcAddressApp[0] = \"${src_ip}\"" -i $config_file
    /usr/bin/yq e ".resources[0].properties.restrictedSrcAddressMgmt[0] = \"${src_ip}\"" -i $config_file
    /usr/bin/yq e ".resources[0].properties.networks.externalNetworkName = \"<UNIQUESTRING>-network1-network\"" -i $config_file
    /usr/bin/yq e ".resources[0].properties.networks.internalNetworkName = \"<UNIQUESTRING>-network2-network\"" -i $config_file
    /usr/bin/yq e ".resources[0].properties.networks.mgmtNetworkName = \"<UNIQUESTRING>-network0-network\"" -i $config_file
    /usr/bin/yq e ".resources[0].properties.subnets.mgmtSubnetName = \"<UNIQUESTRING>-subnet0-subnet\"" -i $config_file
    /usr/bin/yq e ".resources[0].properties.subnets.appSubnetName = \"<UNIQUESTRING>-subnet1-subnet\"" -i $config_file
    /usr/bin/yq e ".resources[0].properties.subnets.internalSubnetName = \"<UNIQUESTRING>-subnet2-subnet\"" -i $config_file
    /usr/bin/yq e ".resources[0].properties.region = \"<REGION>\"" -i $config_file
    /usr/bin/yq e ".resources[0].properties.uniqueString = \"<UNIQUESTRING>\"" -i $config_file
    /usr/bin/yq e ".resources[0].type = \"<TEMPLATE NAME>\"" -i $config_file
else 
    echo "Using full stack"

    # Run GDM quickstart template
    cp f5-google-gdm-templates-v2-main/examples/quickstart/sample_quickstart.yaml $config_file

    # Update Config File using sample_quickstart.yaml
    /usr/bin/yq e ".resources[0].name = \"quickstart-py\"" -i $config_file
    /usr/bin/yq e ".resources[0].properties.restrictedSrcAddressApp[0] = \"${src_ip}\"" -i $config_file
    /usr/bin/yq e ".resources[0].properties.restrictedSrcAddressMgmt[0] = \"${src_ip}\"" -i $config_file
    /usr/bin/yq e ".resources[0].properties.region = \"<REGION>\"" -i $config_file
    /usr/bin/yq e ".resources[0].properties.uniqueString = \"<UNIQUESTRING>\"" -i $config_file
fi

# print out config file
/usr/bin/yq e $config_file
labels="delete=true"
gcloud="gcloud deployment-manager deployments create <STACK NAME> --labels $labels --config $config_file"
$gcloud
