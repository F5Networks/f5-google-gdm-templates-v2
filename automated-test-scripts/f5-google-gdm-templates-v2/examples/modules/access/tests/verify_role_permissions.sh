#  expectValue = "ROLE PERMISSIONS PASSED"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 3

rolename=`echo <UNIQUESTRING> | sed 's/-//g'`

gcloud iam roles describe ${rolename}bigipaccessrole --project $GOOGLE_PROJECT_ID --format json > foundPermissions.json

python automated-test-scripts/f5-google-gdm-templates-v2/examples/modules/access/tests/compare_permissions.py <SOLUTION TYPE>
