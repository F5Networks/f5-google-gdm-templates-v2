#!/usr/bin/env bash
#  expectValue = "Created"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0

gcloud compute target-pools create <STACK NAME>-tp \
    --region <REGION>
