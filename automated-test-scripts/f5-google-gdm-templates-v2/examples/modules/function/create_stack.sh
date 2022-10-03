#  expectValue = "completed successfully"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 0

# set vars
TMP_DIR="/tmp/<DEWPOINT JOB ID>"
tmpl_file='/tmp/function.py'
runtime_file='<RUNTIME INIT>'

# grab template and schema
curl -k <TEMPLATE URL> -o $tmpl_file
curl -k <TEMPLATE URL>.schema -o "${tmpl_file}.schema"

# Run GDM Function template
/usr/bin/yq e -n ".imports[0].path = \"${tmpl_file}\"" > <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].name = \"function\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].type = \"function.py\"" -i <DEWPOINT JOB ID>.yaml

/usr/bin/yq e ".resources[0].properties.uniqueString = \"<UNIQUESTRING>\"" -i <DEWPOINT JOB ID>.yaml

# Adding schedule job
/usr/bin/yq e ".resources[0].properties.jobs[0].name = \"job-<DEWPOINT JOB ID>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.jobs[0].schedule = \"* * * * *\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.jobs[0].timeZone = \"America/Los_Angeles\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.jobs[0].pubsubTarget.topicName = \"projects/f5-7656-pdsoleng-dev/topics/topic-<DEWPOINT JOB ID>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.jobs[0].pubsubTarget.data = \"VGhpcyBteSBoZWxsbyBtZXNzYWdl\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.jobs[0].labels.delete = \"true\"" -i <DEWPOINT JOB ID>.yaml

# Adding PubSub
/usr/bin/yq e ".resources[0].properties.topics[0].name = \"projects/f5-7656-pdsoleng-dev/topics/topic-<DEWPOINT JOB ID>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.topics[0].topic = \"topic-<DEWPOINT JOB ID>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.topics[0].labels.delete = \"true\"" -i <DEWPOINT JOB ID>.yaml

# Adding Cloud Function
/usr/bin/yq e ".resources[0].properties.functions[0].name = \"func-<DEWPOINT JOB ID>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.functions[0].serviceAccountEmail = \"f5-7656-pdsoleng-dev@appspot.gserviceaccount.com\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.functions[0].sourceArchiveUrl = \"gs://f5-gcp-bigiq-revoke-us/develop/v1.0.0/cloud_functions_bigiq_revoke.zip\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.functions[0].entryPoint = \"revoke_bigiq_pubsub\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.functions[0].eventTrigger.eventType = \"google.pubsub.topic.publish\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.functions[0].eventTrigger.resource = \"projects/f5-7656-pdsoleng-dev/topics/topic-<DEWPOINT JOB ID>\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.functions[0].runtime = \"python37\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.functions[0].maxInstances = 10" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.functions[0].environmentVariables.bigIpRuntimeInitConfig = \"https://storage.googleapis.com/<STACK NAME>-bucket/${runtime_file}\"" -i <DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.functions[0].labels.delete = \"true\"" -i <DEWPOINT JOB ID>.yaml

# print out config file
/usr/bin/yq e <DEWPOINT JOB ID>.yaml

labels="delete=true"

gcloud="gcloud deployment-manager deployments create <STACK NAME> --labels $labels --config <DEWPOINT JOB ID>.yaml"
$gcloud
