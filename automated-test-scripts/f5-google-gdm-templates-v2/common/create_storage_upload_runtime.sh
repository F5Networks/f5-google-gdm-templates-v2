#  expectValue = "completed successfully"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 0

# copy local runtime config b4 making changes
cp $PWD/examples/quickstart/bigip-configurations/runtime-init-conf-<NUMBER NICS>nic-<LICENSE TYPE>.yaml $PWD/examples/quickstart/bigip-configurations/<STACK NAME>-config.yaml
cp $PWD/examples/quickstart/bigip-configurations/runtime-init-conf-<NUMBER NICS>nic-<LICENSE TYPE>-with-app.yaml $PWD/examples/quickstart/bigip-configurations/<STACK NAME>-config-with-app.yaml

# Disable AutoPhoneHome
/usr/bin/yq e ".extension_services.service_operations.[0].value.Common.My_System.autoPhonehome = false" -i $PWD/examples/quickstart/bigip-configurations/<STACK NAME>-config.yaml
/usr/bin/yq e ".extension_services.service_operations.[0].value.Common.My_System.autoPhonehome = false" -i $PWD/examples/quickstart/bigip-configurations/<STACK NAME>-config-with-app.yaml

if [[ "<PROVISION DEMO APP>" == "True" ]]; then
    # Use local files for waf policies
    /usr/bin/yq e ".extension_services.service_operations.[1].value.Tenant_1.Shared.Custom_WAF_Policy.url = \"https://storage.googleapis.com/<STACK NAME>-bucket/bigip-configurations/Rapid_Deployment_Policy_13_1.xml\"" -i $PWD/examples/quickstart/bigip-configurations/<STACK NAME>-config-with-app.yaml
fi

# Uncomment this 2 debug
# /usr/bin/yq e ".controls.logLevel = \"silly\"" -i $PWD/examples/quickstart/bigip-configurations/<STACK NAME>-config.yaml

# Create Bucket, copy local files to bucket, add reaper label, and make files public
gsutil mb gs://<STACK NAME>-bucket
gsutil cp -r file://$PWD/examples/quickstart/bigip-configurations gs://<STACK NAME>-bucket
gsutil label ch -l delete:true gs://<STACK NAME>-bucket
gsutil acl -r ch -u AllUsers:R gs://<STACK NAME>-bucket/bigip-configurations
# Remove modified file from local files
rm $PWD/examples/quickstart/bigip-configurations/<STACK NAME>-config.yaml
rm $PWD/examples/quickstart/bigip-configurations/<STACK NAME>-config-with-app.yaml
if [ $? -eq 0 ]; then
    echo "completed successfully"
fi
