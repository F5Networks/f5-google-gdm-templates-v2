#  expectValue = 'AUTO_PASSED'
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 5

mkdir -p /tmp/<DEWPOINT JOB ID>
echo "template url: https://raw.githubusercontent.com/F5Networks/f5-aws-cloudformation-v2/main/examples/modules/network/network.yaml"

curl -k https://raw.githubusercontent.com/F5Networks/f5-aws-cloudformation-v2/main/examples/modules/network/network.yaml -o /tmp/<DEWPOINT JOB ID>/network.yaml

echo "uploading local bigiq template"
curl -k file://$PWD/automated-test-scripts/f5-google-gdm-templates-v2/common/f5-existing-stack-byol-2nic-bigiq-licmgmt.template -o /tmp/<DEWPOINT JOB ID>/f5-existing-stack-byol-2nic-bigiq-licmgmt.template


# r=$(date +%s | sha256sum | base64 | head -c 32)
bucket_name=`echo <STACK NAME>-gcp-test|cut -c -60|tr '[:upper:]' '[:lower:]'| sed 's:-*$::'`
aws s3 mb --region us-west-1 s3://"$bucket_name"
aws s3api put-bucket-tagging --bucket $bucket_name  --tagging 'TagSet=[{Key=delete,Value=True},{Key=creator,Value=dewdrop}]'
#aws s3 cp /tmp/<TEMPLATE NAME> s3://"$bucket_name"
OUTPUT=$(aws s3 cp --region us-west-1 /tmp/<DEWPOINT JOB ID>/network.yaml s3://"$bucket_name" 2>&1)
BIGIQ_OUTPUT=$(aws s3 cp --region us-west-1 /tmp/<DEWPOINT JOB ID>/f5-existing-stack-byol-2nic-bigiq-licmgmt.template s3://"$bucket_name" 2>&1)
echo '------'
echo "OUTPUT = $OUTPUT"
echo "BIGIQ_OUTPUT = $BIGIQ_OUTPUT"
echo '------'
if grep -q failed <<< "$OUTPUT" ; then
    echo AUTO_FAILED
elif grep -q failed <<< "$BIGIQ_OUTPUT" ; then
    echo AUTO_FAILED
else
	echo AUTO_PASSED
fi