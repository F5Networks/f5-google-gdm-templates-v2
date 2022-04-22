#  expectValue = "completed successfully"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0


# this script creates the "pre-existing" internet > bastion firewall rule 
# when deploying existing stack templates w/o public IP
# set vars
TMP_DIR="/tmp/<DEWPOINT JOB ID>"
tmpl_file='/tmp/dag.py'

# grab template and schema
curl -k <DAG TEMPLATE URL> -o $tmpl_file
curl -k <DAG TEMPLATE URL>.schema -o "${tmpl_file}.schema"

if echo "<TEMPLATE URL>" | grep "autoscale"; then
    mgmtNetworkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<UNIQUESTRING>-network-network" '.[] | select(.name | contains($n)) | .selfLink')
else
    mgmtNetworkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<UNIQUESTRING>-network0-network" '.[] | select(.name | contains($n)) | .selfLink')
fi
src_ip_mgmt=$(curl ifconfig.me)/32
echo "mgmt network: ${mgmtNetworkSelfLink}"
echo "source IP: ${src_ip_mgmt}"

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
/usr/bin/yq e ".resources[0].properties.firewalls[0].description = \"Allow ssh and 443 to bastion\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.firewalls[0].name = \"<UNIQUESTRING>-bastion-fw\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.firewalls[0].network = \"$mgmtNetworkSelfLink\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.firewalls[0].sourceRanges[0] = \"${src_ip_mgmt}\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.firewalls[0].targetTags[0] = \"<UNIQUESTRING>-bastion-fw\"" -i <DEWPOINT JOB ID>.yaml


# print out config file
/usr/bin/yq e <DEWPOINT JOB ID>.yaml

labels="delete=true"

gcloud="gcloud deployment-manager deployments create <DAG STACK NAME> --labels $labels --config <DEWPOINT JOB ID>.yaml"
$gcloud
