#  expectValue = "license valid"
#  scriptTimeout = 5
#  replayEnabled = true
#  replayTimeout = 60


LICENSE_HOST=$(aws cloudformation describe-stacks --region us-west-1 --stack-name <STACK NAME>-bigiq-gcp-test|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="device1Url")|.OutputValue|split(":")[1]|.[2:]')
echo "BigiqPublicIP=$LICENSE_HOST"
sshpass -p 'b1gAdminPazz' ssh -o StrictHostKeyChecking=no admin@${LICENSE_HOST} 'bash set-basic-auth on'
ACTIVATED=$(curl -skvvu admin:'b1gAdminPazz' https://${LICENSE_HOST}/mgmt/cm/device/licensing/pool/utility/licenses | jq .items[0].status)


if [[ $ACTIVATED == \"READY\" ]]; then
echo "license valid"
else
echo "Status: $ACTIVATED"
echo "sleep 2 minutes before retry"
sleep 120
fi