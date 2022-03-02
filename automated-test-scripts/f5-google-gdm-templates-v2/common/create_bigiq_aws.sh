#!/usr/bin/env bash
#  expectValue = "StackId"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 0

echo "license type: <LICENSE TYPE>"
bigiq_lic_pool="<BIGIQ LICENSE POOL>"
bigiq_lic_key="<AUTOFILL CLPV2 LICENSE KEY>"
# Capture environment ids required to create stack
vpc=$(aws cloudformation describe-stacks --region us-west-1 --stack-name <STACK NAME>-gcp-test | jq -r '.Stacks[].Outputs[] |select (.OutputKey=="vpcId")|.OutputValue')
echo "VPC:$vpc"
subnetAz1=$(aws cloudformation describe-stacks --region us-west-1 --stack-name <STACK NAME>-gcp-test | jq  -r '.Stacks[0].Outputs[] | select(.OutputKey=="subnetsA").OutputValue' | cut -d ',' -f 1)
subnetAz1_2=$(aws cloudformation describe-stacks --region us-west-1 --stack-name <STACK NAME>-gcp-test | jq  -r '.Stacks[0].Outputs[] | select(.OutputKey=="subnetsA").OutputValue' | cut -d ',' -f 2)
# use published standalone big-iq template
bucket_name=`echo <STACK NAME>-gcp-test|cut -c -60|tr '[:upper:]' '[:lower:]'| sed 's:-*$::'`
set_bigiq_pass="arn:aws:s3:::bigiqtest/passworddb.json"
source_cidr=0.0.0.0/0
aws cloudformation create-stack --disable-rollback --region us-west-1 --stack-name <STACK NAME>-bigiq-gcp-test --tags Key=creator,Value=dewdrop Key=delete,Value=True \
--template-url https://"$bucket_name".s3-us-west-1.amazonaws.com/f5-existing-stack-byol-2nic-bigiq-licmgmt.template \
--capabilities CAPABILITY_IAM --parameters \
ParameterKey=allowUsageAnalytics,ParameterValue=No \
ParameterKey=Vpc,ParameterValue=$vpc \
ParameterKey=instanceType,ParameterValue=m4.2xlarge \
ParameterKey=restrictedSrcAddress,ParameterValue="$source_cidr" \
ParameterKey=restrictedSrcAddressApp,ParameterValue="$source_cidr" \
ParameterKey=sshKey,ParameterValue=dewpt \
ParameterKey=managementSubnetAz1,ParameterValue=$subnetAz1 \
ParameterKey=subnet1Az1,ParameterValue=$subnetAz1_2 \
ParameterKey=ntpServer,ParameterValue="0.us.pool.ntp.org" \
ParameterKey=timezone,ParameterValue="US/Pacific" \
ParameterKey=bigIqPasswordS3Arn,ParameterValue=$set_bigiq_pass \
ParameterKey=licenseKey1,ParameterValue=<AUTOFILL BIGIQ LICENSE KEY> \
ParameterKey=regPoolKeys,ParameterValue=DO_NOT_CREATE \
ParameterKey=licensePoolKeys,ParameterValue=$bigiq_lic_key
echo "Creating BIGIQ using bigIQ standalone template for test"