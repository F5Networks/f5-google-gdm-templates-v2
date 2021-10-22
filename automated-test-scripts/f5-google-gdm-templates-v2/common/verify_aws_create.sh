#  expectValue = "SUCCESS"
#  expectFailValue = "failed to create:"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 200

bigip=$(aws cloudformation describe-stacks --region us-west-1 --stack-name <STACK NAME>-gcp-test)
events=$(aws cloudformation describe-stack-events --region us-west-1 --stack-name <STACK NAME>-gcp-test|jq '.StackEvents[]|select (.ResourceStatus=="CREATE_FAILED")|(.ResourceType, .ResourceStatusReason)')

if echo $bigip | grep 'CREATE_COMPLETE'; then
  echo "SUCCESS"
else
  echo "FAILED"
  echo "EVENTS:${events}"
fi
