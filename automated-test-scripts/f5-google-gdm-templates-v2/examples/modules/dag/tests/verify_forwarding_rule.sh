#  expectValue = "Successful"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 3

forwardingRuleCountCreated=$(gcloud compute forwarding-rules list --filter="name~'<UNIQUESTRING>'" --format=json | jq length)
forwardingRuleCountRequested=$(( <NUM FORWARDING RULES> ))

internalNetworkSelfLink=$(gcloud compute networks list --format json | jq -r --arg n "<UNIQUESTRING>-network3-network" '.[] | select(.name | contains($n)) | .selfLink')
internalSubnetSelfLink=$(gcloud compute networks subnets list --format json | jq -r --arg n "<UNIQUESTRING>-subnet3-subnet" '.[] | select(.name | contains($n)) | .selfLink')


if [[ $forwardingRuleCountCreated = $forwardingRuleCountRequested ]]; then
    if [[ <NUM INTERNAL FORWARDING RULES> = 0 ]]; then
        echo "Successful"
    else
        # Validating Int Forwarding Rule points to internal network
        testNetworkSelfLink=$(gcloud compute forwarding-rules list --filter="name~'<UNIQUESTRING>'" --format=json | jq '.[] | select(.name=="<UNIQUESTRING>-intfr0-fr") | .network' | tr -d '"')
        if [[ $internalNetworkSelfLink == $testNetworkSelfLink ]]; then
            echo "Successful"
        fi
    fi
fi
