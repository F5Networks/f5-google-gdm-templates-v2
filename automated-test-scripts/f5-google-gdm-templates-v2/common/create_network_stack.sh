#  expectValue = "completed successfully"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0

# set vars
tmpl_file='/tmp/network.py'

# grab template and schema
curl -k <NETWORK TEMPLATE URL> -o $tmpl_file
curl -k <NETWORK TEMPLATE URL>.schema -o "${tmpl_file}.schema"

# Create Base config file with no optional properties
i=0
((c=<NUMBER NETWORKS>-1))
until [ $i -gt $c ]; do
    if [ $i = 0 ]; then
        /usr/bin/yq e -n ".imports[${i}].path = \"${tmpl_file}\"" > <DEWPOINT JOB ID>.yaml
    fi
    /usr/bin/yq e ".resources[${i}].name = \"network${i}\"" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[${i}].type = \"network.py\"" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[${i}].properties.uniqueString = \"<UNIQUESTRING>\"" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[${i}].properties.name = \"network${i}\"" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[${i}].properties.subnets[0].name = \"subnet${i}\"" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[${i}].properties.subnets[0].region = \"<REGION>\"" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[${i}].properties.subnets[0].ipCidrRange = \"10.0.${i}.0/24\"" -i <DEWPOINT JOB ID>.yaml
    ((i=i+1))
done

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
