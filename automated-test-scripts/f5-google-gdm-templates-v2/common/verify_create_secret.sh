#!/usr/bin/env bash
#  expectValue = "SECRET CREATION PASSED"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 3

# Script confirms config file and resources created in gcloud match using network names.

secret_gcloud=$(gcloud secrets describe <STACK NAME>-secret --format json | jq -r --arg n "<STACK NAME>" '. | select(.name | contains($n)) | .name')

echo "$secret_gcloud"

if echo "$secret_gcloud" | grep "secrets"; then
    echo "SECRET CREATION PASSED"
else
    echo "SECRET not created properly"
    echo "Resource Created:$secret_gcloud"
fi