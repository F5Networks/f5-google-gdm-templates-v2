#!/usr/bin/env bash
#  expectValue = "DAG CREATION PASSED"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 3

# Script confirms config file and resources created in gcloud match using network names.

firewall_gcloud=$(gcloud compute firewall-rules list --format json | jq -r --arg n "<DEWPOINT JOB ID>" '.[] | select(.name | contains($n)) | .name')

echo "$firewall_gcloud"

if echo "$firewall_gcloud" | grep "firewall"; then
    echo "DAG CREATION PASSED"
else
    echo "DAG not created properly"
    echo "Resources Created:$firewall_gcloud"
fi