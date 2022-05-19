# Copyright 2021 F5 Networks All rights reserved.
#
# Version 2.2.0.0

# pylint: disable=W,C,R,duplicate-code,line-too-long

"""Creates the dag."""
from collections import OrderedDict
COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'

def populate_properties(context, required_properties, optional_properties):
    properties = {}
    properties.update(
        {
            p: context[p]
            for p in required_properties
        }
    )

    properties.update(
        {
            p: context[p]
            for p in optional_properties
            if p in context.keys()
        }
    )
    return properties


def create_firewall_rule(context):
    """Create firewall rule."""
    # Build firewall property list
    required_properties = [
        'name'
    ]
    optional_properties = [
        'network',
        'description',
        'tags',
        'priority',
        'sourceRanges',
        'destinationRanges',
        'sourceTags',
        'targetTags',
        'sourceServiceAccounts',
        'targetServiceAccounts',
        'allowed',
        'denied',
        'direction',
        'logConfig',
        'disabled'
    ]
    properties = populate_properties(context, required_properties, optional_properties)

    firewall_rule = {
        'name': context.get('name'),
        'type': 'compute.v1.firewall',
        'properties': properties
    }
    return firewall_rule


def create_health_check(context):
    """Create health check."""
    # Build health check property list
    required_properties = [
        'name'
    ]
    optional_properties = [
        'description',
        'checkIntervalSec',
        'timeoutSec',
        'unhealthyThreshold',
        'healthyThreshold',
        'tcpHealthCheck',
        'sslHealthCheck',
        'httpHealthCheck',
        'httpsHealthCheck',
        'http2HealthCheck',
        'grpcHealthCheck',
        'logConfig',
        'type'
    ]
    properties = populate_properties(context, required_properties, optional_properties)
    health_check = {
        'name': context['name'],
        'type': 'compute.v1.healthCheck',
        'properties': properties
    }
    return health_check


def create_forwarding_rule(context):
    """Create forwarding rule."""
    required_properties = [
        'name',
        'region'
    ]
    optional_properties = [
        'description',
        'IPAddress',
        'IPProtocol',
        'portRange',
        'ports',
        'target',
        'loadBalancingScheme',
        'subnetwork',
        'network',
        'backendService',
        'serviceDirectoryRegistrations',
        'serviceLabel',
        'networkTier',
        'labels',
        'labelFingerprint',
        'ipVersion',
        'fingerprint',
        'allPorts',
        'allowGlobalAccess',
        'metadataFilters',
        'isMirroringCollector',
        'pscConnectionStatus'
    ]
    properties = populate_properties(context, required_properties, optional_properties)
    forwarding_rule = {
        'name': context['name'],
        'type': 'compute.v1.forwardingRule',
        'properties': properties
    }
    return forwarding_rule


# move to bigip-autoscale
def create_backend_service(context):
    """Create backend service."""
    required_properties = [
        'name',
        'region'
    ]
    optional_properties = [
        'description',
        'backends',
        'healthChecks',
        'timeoutSec',
        'port',
        'protocol',
        'fingerprint',
        'portName',
        'enableCDN',
        'sessionAffinity',
        'affinityCookieTtlSec',
        'failoverPolicy',
        'loadBalancingScheme',
        'connectionDraining',
        'iap',
        'cdnPolicy',
        'customRequestHeaders',
        'customResponseHeaders',
        'logConfig',
        'securitySettings',
        'localityLbPolicy',
        'consistentHash',
        'circuitBreakers',
        'outlierDetection',
        'network',
        'maxStreamDuration'
    ]
    properties = populate_properties(context, required_properties, optional_properties)
    backend_service = {
        'name': context['name'],
        'type': 'compute.v1.regionBackendService',
        'properties': properties
    }
    return backend_service


def create_firewall_rule_outputs(firewall_rule):
    """Create firewall rule targetTag outputs."""
    firewall_rule_target_tag_outputs = {
        'name': firewall_rule['name'],
        'value': firewall_rule['name']
    }
    return firewall_rule_target_tag_outputs


def create_forwarding_rule_outputs(forwarding_rule):
    """Create forwarding rule outputs."""
    forwarding_rule_outputs = {
        'name': forwarding_rule['name'],
        'value': '$(ref.' + forwarding_rule['name'] + '.IPAddress)'
    }
    return forwarding_rule_outputs


def create_backend_service_output(backend_service):
    """Create backend service outputs."""
    backend_service = {
        'name': 'backendService',
        'resourceName': backend_service['name'],
        'value': '$(ref.' + backend_service['name'] + '.selfLink)',
    }
    return backend_service


def generate_name(prefix, suffix):
    """Generate unique name."""
    return prefix + "-" + suffix


def generate_config(context):
    """Entry point for the deployment resources."""
    name = context.properties.get('name') or \
           context.env['name']

    deployment_name = generate_name(context.properties['uniqueString'], name)
    resources = []
    outputs = [
        {
            'name': 'dagName',
            'value': deployment_name
        }
    ]

    for firewall in context.properties.get('firewalls', []):
        resources.append(create_firewall_rule(firewall))

    for health_check in context.properties.get('healthChecks', []):
        resources.append(create_health_check(health_check))

    for forwarding_rule in context.properties.get('forwardingRules', []):
        resources.append(create_forwarding_rule(forwarding_rule))

    for backend_service in context.properties.get('backendServices', []):
        resources.append(create_backend_service(backend_service))
        outputs.append(create_backend_service_output(backend_service))

    return {
        'resources':
            resources,
        'outputs':
            outputs
    }
