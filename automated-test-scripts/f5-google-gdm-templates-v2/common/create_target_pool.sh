#!/usr/bin/env bash
#  expectValue = "Created"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0

gcloud compute target-pools create <UNIQUESTRING>-bigip-tp \
    --region <REGION>
