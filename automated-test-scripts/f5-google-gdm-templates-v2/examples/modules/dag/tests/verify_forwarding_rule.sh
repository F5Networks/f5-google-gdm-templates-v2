#  expectValue = "Successful"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 3

forwardingRuleCountCreated=$(gcloud compute forwarding-rules list --filter="name~'<STACK NAME>'" --format=json | jq length)
forwardingRuleCountRequested=$(( <NUM FORWARDING RULES> + <NUM INTERNAL FORWARDING RULES> ))

internalNetworkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<DEWPOINT JOB ID>-network2" '.[] | select(.name | contains($n)) | .selfLink')
internalSubnetSelfLink=$(gcloud compute networks subnets list --format json | jq -r --arg n "<DEWPOINT JOB ID>-subnet2" '.[] | select(.name | contains($n)) | .selfLink')


if [[ $forwardingRuleCountCreated = $forwardingRuleCountRequested ]]; then
    if [[ <NUM INTERNAL FORWARDING RULES> = 0 ]]; then
        echo "Successful"
    else
        # Validating Int Forwarding Rule points to internal network
        testNetworkSelfLink=$(gcloud compute forwarding-rules list --filter="name~'<DEWPOINT JOB ID>'" --format=json | jq '.[] | select(.name=="<STACK NAME>-intfr0") | .network' | tr -d '"')
        if [[ $internalNetworkSelfLink == $testNetworkSelfLink ]]; then
            echo "Successful"
        fi
    fi
fi
