#  expectValue = "SUCCESS"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 0
#  expectFailValue = "FAILED"

firewall_rule=$(gcloud compute firewall-rules list --filter="name=('<UNIQUESTRING>-ha-fw')" --format=json | jq -r '.[0].name')

echo "Firewall Rule: $firewall_rule"
echo "Authorizing Firewall Rule for 1026 port on internal interface. This is done to make Active-Standby"

response=$(gcloud compute firewall-rules update <UNIQUESTRING>-ha-fw --no-disabled)
if [ $? -eq 0 ]; then
    echo "SUCCESS"
else
    echo "FAILED"
fi