#  expectValue = "completed successfully"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0

# set vars
tmpl_file='/tmp/network.py'

# grab template and schema
curl -k <NETWORK TEMPLATE URL> -o $tmpl_file
curl -k <NETWORK TEMPLATE URL>.schema -o "${tmpl_file}.schema"

/usr/bin/yq e -n ".imports[0].path = \"${tmpl_file}\"" > <DEWPOINT JOB ID>.yaml

/usr/bin/yq e ".resources[0].name = \"network\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].type = \"network.py\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.uniqueString = \"<UNIQUESTRING>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.name = \"network\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.provisionPublicIp = <PROVISION PUBLIC IP>" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.region = \"<REGION>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.subnets[0].name = \"mgmt\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.subnets[0].region = \"<REGION>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.subnets[0].ipCidrRange = \"10.0.0.0/24\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.subnets[1].name = \"app\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.subnets[1].region = \"<REGION>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.subnets[1].ipCidrRange = \"10.0.1.0/24\"" -i <DEWPOINT JOB ID>.yaml


# Modify base config to add in optional properties - only for first network
enable_flow_logs="<ENABLE FLOW LOGS>"
private_ip_google_access="<PRIVATE IP GOOGLE ACCESS>"
description="<DESCRIPTION>"
range_name1="<SECONDARY RANGE NAME 1>"
ip_cidr_range1="<SECONDARY IP CIDR RANGE 1>"
if [ -n "$enable_flow_logs" ] && [ "$enable_flow_logs" != null ]; then
    /usr/bin/yq e ".resources[0].properties.subnets[0].enableFlowLogs = ${enable_flow_logs}" -i <DEWPOINT JOB ID>.yaml
fi
if [ -n "$private_ip_google_access" ] && [ "$private_ip_google_access" != null ]; then
    /usr/bin/yq e ".resources[0].properties.subnets[0].privateIpGoogleAccess = ${private_ip_google_access}" -i <DEWPOINT JOB ID>.yaml
fi
if [ -n "$description" ] && [ "$description" != null ]; then
    /usr/bin/yq e ".resources[0].properties.subnets[0].description = \"${description}\"" -i <DEWPOINT JOB ID>.yaml
fi
if [ -n "$range_name1" ] && [ "$range_name1" != null ]; then
    /usr/bin/yq e ".resources[0].properties.subnets[0].secondaryIpRanges[0].rangeName = \"$range_name1\"" -i <DEWPOINT JOB ID>.yaml
fi
if [ -n "$ip_cidr_range1" ] && [ "$ip_cidr_range1" != null ]; then
    /usr/bin/yq e ".resources[0].properties.subnets[0].secondaryIpRanges[0].ipCidrRange = \"${ip_cidr_range1}\"" -i <DEWPOINT JOB ID>.yaml
fi

# print out config file
/usr/bin/yq e <DEWPOINT JOB ID>.yaml

labels="delete=true"

gcloud="gcloud deployment-manager deployments create <NETWORK STACK NAME> --labels $labels --config <DEWPOINT JOB ID>.yaml"
$gcloud
