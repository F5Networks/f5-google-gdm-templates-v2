#  expectValue = "completed successfully"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 0


if [[ "<PROVISION DEMO APP>" == "True" ]]; then
    gcloud deployment-manager deployments delete <APPLICATION STACK NAME> -q
else
    echo "completed successfully"
fi