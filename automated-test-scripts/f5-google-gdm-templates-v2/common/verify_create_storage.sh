#  expectValue = "STORAGE BUCKET CREATION PASSED"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 0
bucket=`gsutil ls | grep '<STACK NAME>-bucket'`

if echo "$bucket" | grep "gs"; then
    echo "STORAGE BUCKET CREATION PASSED"
else
    echo "STORAGE BUCKET not created properly"
    echo "Resource Created:$bucket"
fi
