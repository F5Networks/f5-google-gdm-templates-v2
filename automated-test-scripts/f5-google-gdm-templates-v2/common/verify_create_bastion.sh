#  expectValue = "COMPLETED"
#  expectFailValue = "FAILED"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 30

if [[ "<PROVISION PUBLIC IP>" == "False" ]]; then
    gcloud deployment-manager deployments describe <BASTION STACK NAME>
else
    echo "COMPLETED"
fi