#  expectValue = "completed successfully"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 0

gsutil mb gs://<STACK NAME>-bucket

if [ $? -eq 0 ]; then
    echo "completed successfully"
fi
