#  expectValue = "is not found"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 5

if [[ "<PROVISION DEMO APP>" == "True" ]]; then
    gcloud deployment-manager deployments describe <APPLICATION STACK NAME>
else
    echo "is not found"
fi