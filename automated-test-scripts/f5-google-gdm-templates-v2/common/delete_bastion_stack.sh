#  expectValue = "completed successfully"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 0


if [[ "<PROVISION PUBLIC IP>" == "False" ]]; then
    gcloud deployment-manager deployments delete <BASTION STACK NAME> -q
else
    echo "completed successfully"
fi

