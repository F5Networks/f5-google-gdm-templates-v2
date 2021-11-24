#  expectValue = "Created"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0

gcloud secrets create <STACK NAME>-secret

echo -n "<AUTOFILL PASSWORD>" | gcloud secrets versions add <STACK NAME>-secret --data-file=-