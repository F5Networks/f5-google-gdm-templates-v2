#!/usr/bin/env bash
#  expectValue = "SUBNET CREATION PASSED"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 3

# Script confirms config file and resources created in gcloud match using subnet names.
subnet_name=($(/usr/bin/yq e .resources[].properties.subnets[].name <DEWPOINT JOB ID>.yaml))
unique_string=$(/usr/bin/yq e .resources[0].properties.uniqueString <DEWPOINT JOB ID>.yaml)
dash="-"
subnetss=()
for i in "${subnet_name[@]}"; do
    subnets+=("$unique_string$dash$i")
done
subnets_gcloud=$(gcloud compute networks subnets list --format json | jq -r --arg n "<DEWPOINT JOB ID>" '.[] | select(.name | contains($n)) | .name')


# Script confirms config file and resources created in gcloud match using cidr values.
subnets_cidr=$(/usr/bin/yq e .resources[].properties.subnets[].ipCidrRange <DEWPOINT JOB ID>.yaml)
subnets_gcloud_cidr=$(gcloud compute networks subnets list --format json | jq -r --arg n "<DEWPOINT JOB ID>" '.[] | select(.name | contains($n)) | .ipCidrRange')

# Script confirms config file and resources created in gcloud match using region values.
subnets_region=$(/usr/bin/yq e .resources[].properties.subnets[].region <DEWPOINT JOB ID>.yaml)
subnets_gcloud_region=$(gcloud compute networks subnets list --format json | jq -r --arg n "<DEWPOINT JOB ID>" '.[] | select(.name | contains($n)) | .region'| cut -d"/" -f9)

if echo "${subnets[*]}" | grep "$subnets_gcloud" && [ "$subnets_cidr" == "$subnets_gcloud_cidr" ] && [ "$subnets_region" == "$subnets_gcloud_region" ]; then
    echo "SUBNET CREATION PASSED"
else
    echo "Subnets properties do not match"
    echo "Config file name:${subnet_name[*]}"
    echo "Resources returned name:$subnets_gcloud"
    echo "Config file cidr:$subnets_cidr"
    echo "Resources returned cidr:$subnets_gcloud_cidr"
    echo "Config file region:$subnets_region"
    echo "Resources returned region:$subnets_gcloud_region"
fi