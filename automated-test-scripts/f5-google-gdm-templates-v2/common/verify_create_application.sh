#  expectValue = "COMPLETED"
#  expectFailValue = "FAILED"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 30

if [[ "<PROVISION DEMO APP>" == "True" ]]; then
    gcloud deployment-manager deployments describe <APPLICATION STACK NAME>
else
    echo "COMPLETED"
fi