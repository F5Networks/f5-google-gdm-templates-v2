# Copyright 2021 F5 Networks All rights reserved.
#
# Version 0.1.0
"""Creates the dag """
from collections import OrderedDict
COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'

def create_firewall_rule_mgmt(context):
    """ Create firewall rule for mgmt """
    source_list = str(context.properties['restrictedSrcAddressMgmt']).split()
    firewall_rule_mgmt = {
        'name': 'mgmtfw-' + context.env['deployment'],
        'type': 'compute.v1.firewall',
        'properties': {
            'network': context.properties['networkSelfLinkMgmt'],
            'sourceRanges': source_list,
            'targetTags': ['mgmtfw-' + context.env['deployment']],
            'allowed': [{
                "IPProtocol": "TCP",
                "ports": [str(context.properties['guiPortMgmt']), '22'],
            },
            ]
        }
    }
    return firewall_rule_mgmt


def create_firewall_rule_app(context):
    """ Create firewall rule for application """
    ports = str(context.properties['applicationPort'])
    if int(context.properties['numberOfInternalForwardingRules']) != 0:
        ports = ports + ' ' + str(context.properties['applicationInternalPort'])
    ports = ports.split()
    ports = list(OrderedDict.fromkeys(ports))
    source_list = str(context.properties['restrictedSrcAddressApp'])
    if int(context.properties['numberOfInternalForwardingRules']) != 0:
        source_list = source_list + ' ' + str(context.properties['restrictedSrcAddressAppInternal'])
    source_list = source_list.split()
    source_list = list(OrderedDict.fromkeys(source_list))
    firewall_rule_app = {
        'name': 'appfw-' + context.env['deployment'],
        'type': 'compute.v1.firewall',
        'properties': {
            'network': context.properties['networkSelfLinkExternal'],
            'sourceRanges': source_list,
            'targetTags': ['appfw-'+ context.env['deployment']],
            'allowed': [{
                "IPProtocol": "TCP",
                "ports": ports,
            },
            ]
        }
    }
    return firewall_rule_app


def create_health_check(context, source):
    """ Create health check """
    if source == "internal":
        health_check = {
            'name': context.env['deployment'] + '-' + source,
            'type': 'compute.v1.healthCheck',
            'properties': {
                'type': 'TCP',
                'tcpHealthCheck': {
                    'port': int(context.properties['applicationPort'])
                }
            }
        }
    else:
        health_check = {
            'name': context.env['deployment'] + '-' + source,
            'type': 'compute.v1.httpHealthCheck',
            'properties': {
                'port': int(context.properties['applicationPort'])
            }
        }

    return health_check


def create_target_pool(context):
    """ Create target pool """
    target_pool = {
        'name': context.env['deployment'] + '-tp',
        'type': 'compute.v1.targetPool',
        'properties': {
            'region': context.properties['region'],
            'sessionAffinity': 'CLIENT_IP',
            'instances': context.properties['instances'],
            'healthChecks': ['$(ref.' + context.env['deployment'] + '-external.selfLink)'],
        }
    }
    return target_pool


def create_forwarding_rule(context, name):
    """ Create forwarding rule """
    forwarding_rule = {
        'name': name,
        'type': 'compute.v1.forwardingRule',
        'properties': {
            'region': context.properties['region'],
            'IPProtocol': 'TCP',
            'target': '$(ref.' + context.env['deployment'] + '-tp.selfLink)',
            'loadBalancingScheme': 'EXTERNAL',
        }
    }
    return forwarding_rule


def create_int_forwarding_rule(context, name):
    """ Create internal forwarding rule """
    ports = str(context.properties['applicationInternalPort']).split()
    int_forwarding_rule = {
        'name': name,
        'type': 'compute.v1.forwardingRule',
        'properties': {
            'description': 'Internal forwarding rule used for BIG-IP LB',
            'region': context.properties['region'],
            'IPProtocol': 'TCP',
            'ports': ports,
            'backendService': '$(ref.' + context.env['deployment'] + '-bes.selfLink)',
            'loadBalancingScheme': 'INTERNAL',
            'network': context.properties['networkSelfLinkInternal'],
            'subnetwork': context.properties['subnetSelfLinkInternal']
        }
    }
    return int_forwarding_rule


def create_backend_service(context):
    """ Create backend service """
    backend_service = {
        'name': context.env['deployment'] + '-bes',
        'type': 'compute.v1.regionBackendService',
        'properties': {
            'description': 'Backend service used for internal LB',
            "backends": [
                {
                    "group": context.properties['instance-groups'][0],
                }
            ],
            'healthChecks': ['$(ref.' + context.env['deployment'] + '-internal.selfLink)'],
            'sessionAffinity': 'CLIENT_IP',
            'loadBalancingScheme': 'INTERNAL',
            'protocol': 'TCP',
            'region': context.properties['region'],
            'network': context.properties['networkSelfLinkInternal']
        },
    }
    return backend_service


# Outputs

def create_forwarding_rule_outputs(name, number_postfix):
    """ Create forwarding rule outputs """
    forwarding_rule_outputs = {
        'name': 'appTrafficAddress' + number_postfix,
        'value': '$(ref.' + name + '.IPAddress)'
    }
    return forwarding_rule_outputs


def create_internal_forwarding_rule_outputs(name, number_postfix):
    """ Create forwarding rule outputs """
    forwarding_rule_outputs = {
        'name': 'internalTrafficAddress' + number_postfix,
        'value': '$(ref.' + name + '.IPAddress)'
    }
    return forwarding_rule_outputs

def create_target_pool_outputs(context):
    """ Create target pool outputs """
    target_pool = {
        'name': 'targetPool',
        'resourceName': context.env['deployment'] + '-tp',
        'value': '$(ref.' + context.env['deployment'] + '-tp.selfLink)'
    }
    return target_pool


def create_backend_service_output(context):
    """ Create backend service outputs """
    backend_service = {
        'name': 'backendService',
        'resourceName': context.env['deployment'] + '-bes',
        'value': '$(ref.' + context.env['deployment'] + '-bes.selfLink)',
    }
    return backend_service

def generate_name(prefix, suffix):
    """ Generate unique name """
    return prefix + "-" + suffix


def generate_config(context):
    """ Entry point for the deployment resources. """

    name = context.properties.get('name') or \
           context.env['name']

    deployment_name = generate_name(context.properties['uniqueString'], name)

    forwarding_rules = []
    forwarding_rule_outputs = []
    for i in list(range(int(context.properties['numberOfForwardingRules']))):
        forwarding_rules = forwarding_rules \
                          + [create_forwarding_rule(
            context,
            context.env['deployment'] + '-fr' + str(i)
        )]
        forwarding_rule_outputs = forwarding_rule_outputs \
                                + [create_forwarding_rule_outputs(
            context.env['deployment'] + '-fr' + str(i),
            str(i)
        )]
    if context.properties['numberOfInternalForwardingRules'] != 0:
        int_forwarding_rules = []
        for i in list(range(int(context.properties['numberOfInternalForwardingRules']))):
            int_forwarding_rules = int_forwarding_rules \
                                 + [create_int_forwarding_rule(
                context,
                context.env['deployment'] + '-intfr' + str(i)
            )]
            forwarding_rule_outputs = forwarding_rule_outputs \
                                    + [create_internal_forwarding_rule_outputs(
                context.env['deployment'] + '-intfr' + str(i),
                str(i)
            )]
        internal_resources = [create_backend_service(context)]
        internal_resources = internal_resources \
                            + [create_health_check(context, "internal")]
    else:
        internal_resources = []
        int_forwarding_rules = []


    resources = [
        create_firewall_rule_mgmt(context),
        create_firewall_rule_app(context),
        create_target_pool(context),
        create_health_check(context, 'external')
    ]

    # add internal lb resources when numberOfIntForwardingRules not equal to 0
    resources = resources + internal_resources
    # add forwarding rules
    resources = resources + forwarding_rules
    resources = resources + int_forwarding_rules

    outputs = [
        {
            'name': 'dagName',
            'value': deployment_name
        },
        {
            'name': 'region',
            'value': context.properties['region']
        }
    ]
    outputs = outputs + forwarding_rule_outputs
    if context.properties['numberOfForwardingRules'] != 0:
        outputs = outputs + [create_target_pool_outputs(context)]
    if context.properties['numberOfInternalForwardingRules'] != 0:
        outputs = outputs + [create_backend_service_output(context)]


    return {
        'resources':
            resources,
        'outputs':
            outputs
    }
