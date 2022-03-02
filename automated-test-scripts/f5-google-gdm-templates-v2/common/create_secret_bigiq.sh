#  expectValue = "Created"
#  expectFailValue = "Failed"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0


TMP_DIR='/tmp/<DEWPOINT JOB ID>'

SECRET_VALUE='<SECRET VALUE>'
if [[ "<LICENSE TYPE>" == "bigiq" ]]; then
    if [ -f "${TMP_DIR}/bigiq_info.json" ]; then
        echo "Found existing BIG-IQ"
        cat ${TMP_DIR}/bigiq_info.json
        bigiq_address=$(cat ${TMP_DIR}/bigiq_info.json | jq -r .bigiq_address)
        bigiq_password=$(cat ${TMP_DIR}/bigiq_info.json | jq -r .bigiq_password)
    else
        echo "Failed - No BIG-IQ found"
    fi
    SECRET_VALUE=$bigiq_password
fi

gcloud secrets create <STACK NAME>-secret
echo -n ${SECRET_VALUE} | gcloud secrets versions add <STACK NAME>-secret --data-file=-
