#  expectValue = "completed successfully"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0

# set vars
TMP_DIR="/tmp/<DEWPOINT JOB ID>"
tmpl_file='/tmp/application.py'

if [[ "<PROVISION DEMO APP>" == "True" ]]; then

    # grab template and schema
    curl -k <APPLICATION TEMPLATE URL> -o $tmpl_file
    curl -k <APPLICATION TEMPLATE URL>.schema -o "${tmpl_file}.schema"
    curl -k file://$PWD/examples/modules/application/sample_application.yaml -o /tmp/sample_application.yaml
    curl -k file://$PWD/examples/modules/application/sample_application_autoscale.yaml -o /tmp/sample_application_autoscale.yaml
    # source test functions
    source ${TMP_DIR}/test_functions.sh

    if [[ <NUMBER NETWORKS> == 1 ]]; then
        networkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<UNIQUESTRING>-network0-network" '.[] | select(.name | contains($n)) | .selfLink')
        subnetSelfLink=$(gcloud compute networks subnets list --format json | jq -r --arg n "<UNIQUESTRING>-subnet1-subnet" '.[] | select(.name | contains($n)) | .selfLink')
    elif [[ <NUMBER NETWORKS> == 2 ]]; then
        networkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<UNIQUESTRING>-network1-network" '.[] | select(.name | contains($n)) | .selfLink')
        subnetSelfLink=$(gcloud compute networks subnets list --format json | jq -r --arg n "<UNIQUESTRING>-subnet2-subnet" '.[] | select(.name | contains($n)) | .selfLink')
    elif [[ <NUMBER NETWORKS> == 3 ]]; then
        networkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<UNIQUESTRING>-network2-network" '.[] | select(.name | contains($n)) | .selfLink')
        subnetSelfLink=$(gcloud compute networks subnets list --format json | jq -r --arg n "<UNIQUESTRING>-subnet3-subnet" '.[] | select(.name | contains($n)) | .selfLink')
    fi


    # Run GDM app template
    if [ "<AUTOSCALE>" == "False" ]; then
        cp /tmp/sample_application.yaml <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e -n ".imports[0].path = \"${tmpl_file}\"" > <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].name = \"application\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].type = \"/tmp/application.py\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.appContainerName = \"<APP CONTAINER NAME>\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.instanceType = \"<INSTANCE TYPE>\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.instances[0].name = \"application-vm-01\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.instances[0].networkInterfaces[0].accessConfigs[0].name = \"External NAT\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.instances[0].networkInterfaces[0].accessConfigs[0].type = \"ONE_TO_ONE_NAT\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.instances[0].networkInterfaces[0].network = \"$networkSelfLink\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.instances[0].networkInterfaces[0].subnetwork = \"$subnetSelfLink\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.instances[0].zone = \"<AVAILABILITY ZONE>\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.uniqueString = \"<UNIQUESTRING>\"" -i <DEWPOINT JOB ID>.yaml
    else
        cp /tmp/sample_application_autoscale.yaml <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e -n ".imports[0].path = \"${tmpl_file}\"" > <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].name = \"application\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].type = \"/tmp/application.py\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.appContainerName = \"<APP CONTAINER NAME>\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.instanceType = \"<INSTANCE TYPE>\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.instanceTemplateVersion = 1" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.instanceTemplates[0].networkInterfaces[0].accessConfigs[0].name = \"External NAT\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.instanceTemplates[0].networkInterfaces[0].accessConfigs[0].type = \"ONE_TO_ONE_NAT\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.instanceTemplates[0].networkInterfaces[0].network = \"$networkSelfLink\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.instanceTemplates[0].networkInterfaces[0].subnetwork = \"$subnetSelfLink\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.instanceTemplates[0].zone = \"<AVAILABILITY ZONE>\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.instanceGroupManagers[0].zone = \"<AVAILABILITY ZONE>\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.autoscalers[0].zone = \"<AVAILABILITY ZONE>\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.uniqueString = \"<UNIQUESTRING>\"" -i <DEWPOINT JOB ID>.yaml
    fi
    # print out config file
    /usr/bin/yq e <DEWPOINT JOB ID>.yaml

    labels="delete=true"

    gcloud="gcloud deployment-manager deployments create <APPLICATION STACK NAME> --labels $labels --config <DEWPOINT JOB ID>.yaml"
    $gcloud

else
    echo "completed successfully"
fi