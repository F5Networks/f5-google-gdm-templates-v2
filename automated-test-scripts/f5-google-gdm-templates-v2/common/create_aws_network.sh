#  expectValue = "StackId"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 0


bucket_name=`echo <STACK NAME>-gcp-test|cut -c -60|tr '[:upper:]' '[:lower:]'| sed 's:-*$::'`

parameters="\
ParameterKey=numAzs,ParameterValue=1 \
ParameterKey=numSubnets,ParameterValue=2 \
ParameterKey=setPublicSubnet1,ParameterValue=true \
ParameterKey=subnetMask,ParameterValue=24 \
ParameterKey=uniqueString,ParameterValue=dd<DEWPOINT JOB ID> \
ParameterKey=vpcCidr,ParameterValue=10.0.0.0/16 \
ParameterKey=vpcTenancy,ParameterValue=default"


echo "Parameters:$parameters"

aws cloudformation create-stack --disable-rollback --region us-west-1 --stack-name <STACK NAME>-gcp-test --tags Key=creator,Value=dewdrop Key=delete,Value=True \
--template-url https://s3.amazonaws.com/"$bucket_name"/network.yaml \
--capabilities CAPABILITY_IAM --parameters $parameters