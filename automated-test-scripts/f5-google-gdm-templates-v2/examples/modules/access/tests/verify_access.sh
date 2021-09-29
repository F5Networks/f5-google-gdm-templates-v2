#  expectValue = "ACCESS CREATION PASSED"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 3

service_account=$(gcloud iam service-accounts list --filter="displayName ~ <UNIQUESTRING>" --format=json | jq -r --arg n "<UNIQUESTRING>" '.[] | select(.name | contains($n)) | .name')

echo "$service_account"

if echo "$service_account" | grep "serviceAccounts"; then
    echo "ACCESS CREATION PASSED"
fi