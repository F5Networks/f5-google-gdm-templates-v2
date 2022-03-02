#  expectValue = "completed successfully"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 5
bucket=`gsutil ls | grep '<UNIQUESTRING>-cfe-storage'`

# delete all files in bucket and delete bucket
gsutil -m rm -r ${bucket}

if [ $? -eq 0 ]; then
    echo "completed successfully"
fi
