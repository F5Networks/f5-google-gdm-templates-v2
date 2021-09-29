#  expectValue = "completed successfully"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0


# set vars
TMP_DIR="/tmp/<DEWPOINT JOB ID>"
tmpl_file='/tmp/dag.py'

# grab template and schema
curl -k <DAG TEMPLATE URL> -o $tmpl_file
curl -k <DAG TEMPLATE URL>.schema -o "${tmpl_file}.schema"

# source test functions
source ${TMP_DIR}/test_functions.sh

# determine test environment public ip address
source_cidr=$(get_env_public_ip)
echo "source_cidr=$source_cidr"

mgmtNetworkSelfLink=''
mgmtSubnetSelfLink=''
externalNetworkSelfLink=''
externalSubnetSelfLink=''
internalNetworkSelfLink=''
internalSubnetSelfLink=''
appNetworkSelfLink=''
appSubnetSelfLink=''
instances=''
instanceGroupSelfLink=''

mgmtNetworkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<UNIQUESTRING>-network0-network" '.[] | select(.name | contains($n)) | .selfLink')
mgmtSubnetSelfLink=$(gcloud compute networks subnets list --format json | jq -r --arg n "<UNIQUESTRING>-subnet0-subnet" '.[] | select(.name | contains($n)) | .selfLink')

appNetworkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<UNIQUESTRING>-network1" '.[] | select(.name | contains($n)) | .selfLink')
appSubnetSelfLink=$(gcloud compute networks subnets list --format json | jq -r --arg n "<UNIQUESTRING>-subnet1-subnet" '.[] | select(.name | contains($n)) | .selfLink')

if [ <NUMBER NICS> -ge 2 ]; then
    externalNetworkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<UNIQUESTRING>-network2-network" '.[] | select(.name | contains($n)) | .selfLink')
    externalSubnetSelfLink=$(gcloud compute networks subnets list --format json | jq -r --arg n "<UNIQUESTRING>-subnet2-subnet" '.[] | select(.name | contains($n)) | .selfLink')
fi

if [ <NUMBER NICS> -ge 3 ]; then
    internalNetworkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<UNIQUESTRING>-network3-network" '.[] | select(.name | contains($n)) | .selfLink')
    internalSubnetSelfLink=$(gcloud compute networks subnets list --format json | jq -r --arg n "<UNIQUESTRING>-subnet3-subnet" '.[] | select(.name | contains($n)) | .selfLink')
fi

# instances used by the external forwarding rule/target pool
instances=()
response=$(gcloud compute instance-groups list-instances <UNIQUESTRING>-bigip-ig --region <REGION> --format=json | jq -r .[].instance)
for item in $response
do
    instances+=($(echo ${item}))
done

# instances used by the internal forwarding rule/backend service
use_forwarding_rule="<USE FORWARDING RULE>"
use_backend_service="<USE BACKEND SERVICE>"
use_health_checks="<USE HEALTH CHECKS>"

if echo "$use_backend_service" | grep -q "False"; then
    echo "Not using backend services"
else
    instanceGroupSelfLink=$(gcloud compute instance-groups describe <UNIQUESTRING>-bigip-ig --region <REGION> --format=json | jq -r .selfLink)
fi
if echo "$use_forwarding_rule" | grep -q "False"; then
    echo "Not using forwarding rule"
else
    targetPoolSelfLink=$(gcloud compute target-pools describe <UNIQUESTRING>-bigip-tp --region <REGION> --format=json | jq .selfLink | tr -d '"')
fi


# Run GDM Dag template
/usr/bin/yq e -n ".imports[0].path = \"${tmpl_file}\"" > <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].name = \"dag\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].type = \"dag.py\"" -i <DEWPOINT JOB ID>.yaml

/usr/bin/yq e ".resources[0].properties.uniqueString = \"<UNIQUESTRING>\"" -i <DEWPOINT JOB ID>.yaml

# Adding Firewalls
/usr/bin/yq e ".resources[0].properties.firewalls[0].allowed[0].IPProtocol = \"TCP\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.firewalls[0].allowed[0].ports[0] = 22" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.firewalls[0].allowed[0].ports[1] = 8443" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.firewalls[0].allowed[0].ports[2] = 443" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.firewalls[0].description = \"Allow ssh and 443 to management\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.firewalls[0].name = \"<UNIQUESTRING>-mgmt-fw\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.firewalls[0].network = \"$mgmtNetworkSelfLink\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.firewalls[0].sourceRanges.items[0] = 0.0.0.0/0" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.firewalls[0].targetTags[0] = \"<UNIQUESTRING>-mgmtfw\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.firewalls[0].targetTags[1] = \"<UNIQUESTRING>-mgmt-fw\"" -i <DEWPOINT JOB ID>.yaml

/usr/bin/yq e ".resources[0].properties.firewalls[1].allowed[0].IPProtocol = \"TCP\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.firewalls[1].allowed[0].ports[0] = 8443" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.firewalls[1].allowed[0].ports[1] = 443" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.firewalls[1].allowed[0].ports[2] = 80" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.firewalls[1].description = \"Allow web traffic to public network\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.firewalls[1].name = \"<UNIQUESTRING>-app-fw\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.firewalls[1].network = \"$mgmtNetworkSelfLink\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.firewalls[1].sourceRanges.items[0] = 0.0.0.0/0" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.firewalls[1].targetTags[0] = \"<UNIQUESTRING>-app-fw\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.firewalls[1].targetTags[1] = \"<UNIQUESTRING>-app-int-fw\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.firewalls[2].allowed[0].IPProtocol = \"TCP\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.firewalls[2].allowed[0].ports[0] = <APP PORT>" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.firewalls[2].description = \"Allow app web traffic to public network\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.firewalls[2].name = \"<UNIQUESTRING>-app-vip-fw\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.firewalls[2].network = \"$mgmtNetworkSelfLink\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.firewalls[2].sourceRanges.items[0] = 0.0.0.0/0" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.firewalls[2].targetTags[0] = \"<UNIQUESTRING>-app-vip-fw\"" -i <DEWPOINT JOB ID>.yaml


# Adding Forwarding Rule
if echo "$use_forwarding_rule" | grep -q "False"; then
    echo "Not using forwarding rule"
else
    /usr/bin/yq e ".resources[0].properties.forwardingRules[0].name = \"<UNIQUESTRING>-fwrule1\"" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[0].properties.forwardingRules[0].region = \"<REGION>\"" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[0].properties.forwardingRules[0].IPProtocol = \"TCP\"" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[0].properties.forwardingRules[0].target = \"$targetPoolSelfLink\"" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[0].properties.forwardingRules[0].loadBalancingScheme = \"EXTERNAL\"" -i <DEWPOINT JOB ID>.yaml
fi

# Adding Backend Service
if echo "$use_backend_service" | grep -q "False"; then
    echo "Not using backend services"
else
    /usr/bin/yq e ".resources[0].properties.backendServices[0].backends[0].group = \"$instanceGroupSelfLink\"" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[0].properties.backendServices[0].description = \"Backend service used for internal LB\"" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[0].properties.backendServices[0].healthChecks[0] = \"\$(ref.<UNIQUESTRING>-tcp-healthcheck.selfLink)\"" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[0].properties.backendServices[0].loadBalancingScheme = \"INTERNAL\"" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[0].properties.backendServices[0].name = \"<UNIQUESTRING>-bes\"" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[0].properties.backendServices[0].network = \"$mgmtNetworkSelfLink\"" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[0].properties.backendServices[0].protocol = \"TCP\"" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[0].properties.backendServices[0].region = \"<REGION>\"" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[0].properties.backendServices[0].sessionAffinity = \"CLIENT_IP\"" -i <DEWPOINT JOB ID>.yaml
fi

# Adding Health Checks
if echo "$use_health_checks" | grep -q "False"; then
    echo "Not using health checks"
else
    /usr/bin/yq e ".resources[0].properties.healthChecks[0].checkIntervalSec = 5" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[0].properties.healthChecks[0].description = \"my tcp healthcheck\"" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[0].properties.healthChecks[0].name = \"<UNIQUESTRING>-tcp-healthcheck\"" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[0].properties.healthChecks[0].tcpHealthCheck.port = 44000" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[0].properties.healthChecks[0].timeoutSec = 5" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[0].properties.healthChecks[0].type = \"TCP\"" -i <DEWPOINT JOB ID>.yaml

    /usr/bin/yq e ".resources[0].properties.healthChecks[1].checkIntervalSec = 5" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[0].properties.healthChecks[1].description = \"my http healthcheck\"" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[0].properties.healthChecks[1].name = \"<UNIQUESTRING>-http-healthcheck\"" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[0].properties.healthChecks[1].httpHealthCheck.port = 80" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[0].properties.healthChecks[1].timeoutSec = 5" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[0].properties.healthChecks[1].type = \"HTTP\"" -i <DEWPOINT JOB ID>.yaml

    /usr/bin/yq e ".resources[0].properties.healthChecks[2].checkIntervalSec = 5" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[0].properties.healthChecks[2].description = \"my https healthcheck\"" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[0].properties.healthChecks[2].name = \"<UNIQUESTRING>-https-healthcheck\"" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[0].properties.healthChecks[2].httpsHealthCheck.port = 443" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[0].properties.healthChecks[2].timeoutSec = 5" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[0].properties.healthChecks[2].type = \"HTTPS\"" -i <DEWPOINT JOB ID>.yaml
fi
# print out config file
/usr/bin/yq e <DEWPOINT JOB ID>.yaml

labels="delete=true"

gcloud="gcloud deployment-manager deployments create <DAG STACK NAME> --labels $labels --config <DEWPOINT JOB ID>.yaml"
$gcloud
