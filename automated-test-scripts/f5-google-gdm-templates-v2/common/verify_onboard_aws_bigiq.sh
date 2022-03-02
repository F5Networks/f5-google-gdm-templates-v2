#  expectValue = "SUCCESS"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 180

signal="config_complete"
IP=$(aws cloudformation describe-stacks  --region us-west-1 --stack-name <STACK NAME>-bigiq-gcp-test|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="device1Url")|.OutputValue|split(":")[1]|.[2:]')
echo "BigIqPublicIP=$IP"
ssh-keygen -R $IP 2>/dev/null
ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -i /etc/ssl/private/dewpt.pem admin@${IP} 'modify auth user admin shell bash'
response=$(ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -i /etc/ssl/private/dewpt.pem admin@${IP} 'ls -al /config/cloud')
echo "response: $response"

if echo $response | grep $signal; then
  echo "SUCCESS"
else
  echo "FAILED"
  echo "sleep 2 minutes before retry"
  sleep 120
fi
