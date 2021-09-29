#  expectValue = "completed successfully"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 0

# copy local runtime config b4 making changes
cp $PWD/examples/quickstart/bigip-configurations/runtime-init-conf-<NUMBER NICS>nic-<LICENSE TYPE>.yaml $PWD/examples/quickstart/bigip-configurations/<STACK NAME>-config.yaml
# Add lic key if byol
if [[ "<LICENSE TYPE>" == "byol" ]]; then
    /usr/bin/yq e ".extension_services.service_operations.[0].value.Common.My_License.regKey = \"<AUTOFILL EVAL LICENSE KEY>\"" -i $PWD/examples/quickstart/bigip-configurations/<STACK NAME>-config.yaml
fi
# Use local files for waf policies
/usr/bin/yq e ".extension_services.service_operations.[1].value.Tenant_1.HTTP_Service.WAFPolicy.url = \"https://storage.googleapis.com/<STACK NAME>-bucket/bigip-configurations/Rapid_Deployment_Policy_13_1.xml\"" -i $PWD/examples/quickstart/bigip-configurations/<STACK NAME>-config.yaml
/usr/bin/yq e ".extension_services.service_operations.[1].value.Tenant_1.HTTPS_Service.WAFPolicy.url = \"https://storage.googleapis.com/<STACK NAME>-bucket/bigip-configurations/Rapid_Deployment_Policy_13_1.xml\"" -i $PWD/examples/quickstart/bigip-configurations/<STACK NAME>-config.yaml
# Uncomment this 2 debug
# /usr/bin/yq e ".controls.logLevel = \"silly\"" -i $PWD/examples/quickstart/bigip-configurations/<STACK NAME>-config.yaml

# Create Bucket, copy local files to bucket, add reaper label, and make files public
gsutil mb gs://<STACK NAME>-bucket
gsutil cp -r file://$PWD/examples/quickstart/bigip-configurations gs://<STACK NAME>-bucket
gsutil label ch -l delete:true gs://<STACK NAME>-bucket
gsutil acl -r ch -u AllUsers:R gs://<STACK NAME>-bucket/bigip-configurations
# Remove modified file from local files
rm $PWD/examples/quickstart/bigip-configurations/<STACK NAME>-config.yaml
if [ $? -eq 0 ]; then
    echo "completed successfully"
fi
