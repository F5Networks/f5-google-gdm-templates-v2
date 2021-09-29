#  expectValue = "completed successfully"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 0
bucket=`gsutil ls | grep '<STACK NAME>-bucket'`

if [ $? -eq 1 ]; then
    echo "completed successfully"
fi
