#  expectValue = "completed successfully"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0

tmpl_file='/tmp/bigip_standalone.py'

# grab template and schema
curl -k <TEMPLATE URL> -o $tmpl_file
curl -k file://$PWD/examples/modules/bigip-standalone/sample_bigip_standalone.yaml -o /tmp/sample_bigip_standalone.yaml
curl -k <TEMPLATE URL>.schema -o "${tmpl_file}.schema"

# Add lic key if byol
license_key=''
if [[ "<LICENSE TYPE>" == "byol" ]]; then
    license_key='<AUTOFILL EVAL LICENSE KEY>'
fi

# Run GDM bigip-standalone template

# Create Config File
i=0
((c=<NUMBER NICS>-1))
until [ $i -gt $c ]; do
    if [[ $i = 1 ]]; then
        networkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<DEWPOINT JOB ID>-network0" '.[] | select(.name | contains($n)) | .selfLink')
        subnetSelfLink=$(gcloud compute networks subnets list --format json | jq -r --arg n "<DEWPOINT JOB ID>-subnet0" '.[] | select(.name | contains($n)) | .selfLink')
    elif [[ $c = 0 ]]; then
        networkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<DEWPOINT JOB ID>-network0" '.[] | select(.name | contains($n)) | .selfLink')
        subnetSelfLink=$(gcloud compute networks subnets list --format json | jq -r --arg n "<DEWPOINT JOB ID>-subnet0" '.[] | select(.name | contains($n)) | .selfLink')
    elif [[ $i = 0 ]]; then
        networkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<DEWPOINT JOB ID>-network1" '.[] | select(.name | contains($n)) | .selfLink')
        subnetSelfLink=$(gcloud compute networks subnets list --format json | jq -r --arg n "<DEWPOINT JOB ID>-subnet1" '.[] | select(.name | contains($n)) | .selfLink')
    else
        networkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<DEWPOINT JOB ID>-network${i}" '.[] | select(.name | contains($n)) | .selfLink')
        subnetSelfLink=$(gcloud compute networks subnets list --format json | jq -r --arg n "<DEWPOINT JOB ID>-subnet${i}" '.[] | select(.name | contains($n)) | .selfLink')
    fi

    if [ $i = 0 ]; then
        /usr/bin/yq e -n ".imports[0].path = \"${tmpl_file}\"" > <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].name = \"bigip\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.allowUsageAnalytics = False" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.zone = \"<AVAILABILITY ZONE>\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.bigIpRuntimeInitConfig = \"<BIGIP RUNTIME INIT CONFIG>\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.hostname = \"bigip01.local\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.imageName = \"<IMAGE NAME>\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.instanceType = \"<INSTANCE TYPE>\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.licenseKey = \"${license_key}\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.name = \"<INSTANCE NAME>\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.region = \"<REGION>\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.uniqueString = \"<UNIQUESTRING>\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.tags.items[0] = \"<UNIQUESTRING>-mgmtfw\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.tags.items[1] = \"<UNIQUESTRING>-appfw\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].type = \"<TEMPLATE NAME>\"" -i <DEWPOINT JOB ID>.yaml

    fi
    static0='<STATIC 0>'
    static1='<STATIC 1>'
    static2='<STATIC 2>'
    alias_ip_range='<ALIAS IP RANGE>'
    if [ $c -eq 0 ]; then
        /usr/bin/yq e ".resources[0].properties.networkInterfaces[${i}].accessConfigs[0].name = \"Management NAT\"" -i <DEWPOINT JOB ID>.yaml
        /usr/bin/yq e ".resources[0].properties.networkInterfaces[${i}].accessConfigs[0].type = \"ONE_TO_ONE_NAT\"" -i <DEWPOINT JOB ID>.yaml
        if [[ ! -z "${static0}" ]]; then
            /usr/bin/yq e ".resources[0].properties.networkInterfaces[${i}].networkIP = \"${static0}\"" -i <DEWPOINT JOB ID>.yaml
        fi
        if [[ ! -z "${alias_ip_range}" ]]; then
            /usr/bin/yq e ".resources[0].properties.networkInterfaces[${i}].aliasIpRanges[0].ipCidrRange = \"${alias_ip_range}\"" -i <DEWPOINT JOB ID>.yaml
        fi

    fi
    if [ $c -gt 0 ]; then
        if [ $i = 1 ]; then
            /usr/bin/yq e ".resources[0].properties.networkInterfaces[${i}].accessConfigs[0].name = \"Management NAT\"" -i <DEWPOINT JOB ID>.yaml
            /usr/bin/yq e ".resources[0].properties.networkInterfaces[${i}].accessConfigs[0].type = \"ONE_TO_ONE_NAT\"" -i <DEWPOINT JOB ID>.yaml
            if [[ ! -z "${static1}" ]]; then
                /usr/bin/yq e ".resources[0].properties.networkInterfaces[${i}].networkIP = \"${static1}\"" -i <DEWPOINT JOB ID>.yaml
            fi
        elif [ $i = 0 ]; then
            /usr/bin/yq e ".resources[0].properties.networkInterfaces[${i}].accessConfigs[0].name = \"External NAT\"" -i <DEWPOINT JOB ID>.yaml
            /usr/bin/yq e ".resources[0].properties.networkInterfaces[${i}].accessConfigs[0].type = \"ONE_TO_ONE_NAT\"" -i <DEWPOINT JOB ID>.yaml
            if [[ ! -z "${static0}" ]]; then
                /usr/bin/yq e ".resources[0].properties.networkInterfaces[${i}].networkIP = \"${static0}\"" -i <DEWPOINT JOB ID>.yaml
            fi
            if [[ ! -z "${alias_ip_range}" ]]; then
                /usr/bin/yq e ".resources[0].properties.networkInterfaces[${i}].aliasIpRanges[0].ipCidrRange = \"${alias_ip_range}\"" -i <DEWPOINT JOB ID>.yaml
            fi
        elif [[ $i = 2 && ! -z "${static2}" ]]; then
            /usr/bin/yq e ".resources[0].properties.networkInterfaces[${i}].networkIP = \"${static2}\"" -i <DEWPOINT JOB ID>.yaml
        fi
    fi
    /usr/bin/yq e ".resources[0].properties.networkInterfaces[${i}].network = \"${networkSelfLink}\"" -i <DEWPOINT JOB ID>.yaml
    /usr/bin/yq e ".resources[0].properties.networkInterfaces[${i}].subnetwork = \"${subnetSelfLink}\"" -i <DEWPOINT JOB ID>.yaml   
    /usr/bin/yq e ".resources[0].properties.networkInterfaces[${i}].description = \"Interface used for subnetwork ${i}\"" -i <DEWPOINT JOB ID>.yaml
    ((i=i+1))
done

# print out config file
/usr/bin/yq e <DEWPOINT JOB ID>.yaml
labels="delete=true"
gcloud="gcloud deployment-manager deployments create <STACK NAME> --labels $labels --config <DEWPOINT JOB ID>.yaml"
$gcloud
