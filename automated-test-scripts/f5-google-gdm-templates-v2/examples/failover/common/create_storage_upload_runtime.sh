#  expectValue = "completed successfully"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 0

# copy local runtime config b4 making changes
if [[ "<PROVISION DEMO APP>" == "True" ]]; then
    cp $PWD/examples/failover/bigip-configurations/runtime-init-conf-3nic-<LICENSE TYPE>-instance01-with-app.yaml $PWD/examples/failover/bigip-configurations/<STACK NAME>-config.yaml
    cp $PWD/examples/failover/bigip-configurations/runtime-init-conf-3nic-<LICENSE TYPE>-instance02-with-app.yaml $PWD/examples/failover/bigip-configurations/<STACK NAME>-config2.yaml
    # Use local files for waf policies
    /usr/bin/yq e ".extension_services.service_operations.[2].value.Tenant_1.Shared.Custom_WAF_Policy.url = \"https://storage.googleapis.com/<STACK NAME>-bucket/bigip-configurations/Rapid_Deployment_Policy_13_1.xml\"" -i $PWD/examples/failover/bigip-configurations/<STACK NAME>-config.yaml
    /usr/bin/yq e ".extension_services.service_operations.[2].value.Tenant_1.Shared.Custom_WAF_Policy.url = \"https://storage.googleapis.com/<STACK NAME>-bucket/bigip-configurations/Rapid_Deployment_Policy_13_1.xml\"" -i $PWD/examples/failover/bigip-configurations/<STACK NAME>-config2.yaml
else
    cp $PWD/examples/failover/bigip-configurations/runtime-init-conf-3nic-<LICENSE TYPE>-instance01.yaml $PWD/examples/failover/bigip-configurations/<STACK NAME>-config.yaml
    cp $PWD/examples/failover/bigip-configurations/runtime-init-conf-3nic-<LICENSE TYPE>-instance02.yaml $PWD/examples/failover/bigip-configurations/<STACK NAME>-config2.yaml
fi
# Add secret
/usr/bin/yq e ".runtime_parameters.[0].secretProvider.secretId = \"<STACK NAME>-secret\"" -i $PWD/examples/failover/bigip-configurations/<STACK NAME>-config.yaml
/usr/bin/yq e ".runtime_parameters.[0].secretProvider.secretId = \"<STACK NAME>-secret\"" -i $PWD/examples/failover/bigip-configurations/<STACK NAME>-config2.yaml
# Add lic key if byol
if [[ "<LICENSE TYPE>" == "byol" ]]; then
    /usr/bin/yq e ".extension_services.service_operations.[0].value.Common.My_License.regKey = \"<AUTOFILL EVAL LICENSE KEY>\"" -i $PWD/examples/failover/bigip-configurations/<STACK NAME>-config.yaml
    /usr/bin/yq e ".extension_services.service_operations.[0].value.Common.My_License.regKey = \"<AUTOFILL EVAL LICENSE KEY 2>\"" -i $PWD/examples/failover/bigip-configurations/<STACK NAME>-config2.yaml
fi
# Uncomment this 2 debug
# /usr/bin/yq e ".controls.logLevel = \"silly\"" -i $PWD/examples/failover/bigip-configurations/<STACK NAME>-config.yaml

# Create Bucket, copy local files to bucket, add reaper label, and make files public
gsutil mb gs://<STACK NAME>-bucket
gsutil cp -r file://$PWD/examples/failover/bigip-configurations gs://<STACK NAME>-bucket
gsutil label ch -l delete:true gs://<STACK NAME>-bucket
# gsutil label ch -l f5_cloud_failover_label:bigip_high_availability_solution gs://<STACK NAME>-bucket
gsutil acl -r ch -u AllUsers:R gs://<STACK NAME>-bucket/bigip-configurations
# Remove modified file from local files
rm $PWD/examples/failover/bigip-configurations/<STACK NAME>-config.yaml
rm $PWD/examples/failover/bigip-configurations/<STACK NAME>-config2.yaml
if [ $? -eq 0 ]; then
    echo "completed successfully"
fi
