#  expectValue = "SUCCESS"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 150

# Grab stack info based on license type


bigiq=$(aws cloudformation describe-stacks --region us-west-1 --stack-name <STACK NAME>-bigiq-gcp-test)
events=$(aws cloudformation describe-stack-events --region us-west-1 --stack-name <STACK NAME>-bigiq-gcp-test|jq '.StackEvents[]|select (.ResourceStatus=="CREATE_FAILED")|(.ResourceType, .ResourceStatusReason)')
echo "Creating BIGIQ..."

# verify stacks created - verifies both BIGIQ (if created)
if echo $bigiq | grep 'CREATE_COMPLETE'; then
  echo "SUCCESS"
else
  echo "FAILED"
  echo "EVENTS:${events}"
fi
