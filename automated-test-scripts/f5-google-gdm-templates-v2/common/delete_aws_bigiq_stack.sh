#  expectValue = "PASS"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 0

aws cloudformation delete-stack --region us-west-1 --stack-name <STACK NAME>-bigiq-gcp-test
echo "PASS"