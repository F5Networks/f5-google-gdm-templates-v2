# Copyright 2021 F5 Networks All rights reserved.
#
# Version 0.1.0
"""Creates the dag """
from collections import OrderedDict
COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'

def create_firewall_rule(context, config):
    """ Create firewall rule """
    ports = config['ports'].split()
    ports = list(OrderedDict.fromkeys(ports))
    source_list = config['source'].split()
    source_list = list(OrderedDict.fromkeys(source_list))
    firewall_rule = {
        'name': config['prefix'] + context.env['deployment'],
        'type': 'compute.v1.firewall',
        'properties': {
            'network': config['network'],
            'sourceRanges': source_list,
            'targetTags': [config['prefix'] + context.properties['uniqueString']],
            'allowed': [{
                "IPProtocol": "TCP",
                "ports": ports,
            }]
        }
    }
    return firewall_rule


def create_health_check(context, source):
    """ Create health check """
    applicaton_port = str(context.properties['applicationVipPort'])
    applicaton_port = applicaton_port.split()[0]
    if source == "internal":
        health_check = {
            'name': context.env['deployment'] + '-' + source,
            'type': 'compute.v1.healthCheck',
            'properties': {
                'type': 'TCP',
                'tcpHealthCheck': {
                    'port': int(applicaton_port)
                }
            }
        }
    else:
        health_check = {
            'name': context.env['deployment'] + '-' + source,
            'type': 'compute.v1.httpHealthCheck',
            'properties': {
                'port': int(applicaton_port)
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
            'target': context.properties['targetPoolSelfLink'],
            'loadBalancingScheme': 'EXTERNAL',
        }
    }
    return forwarding_rule


def create_int_forwarding_rule(context, name):
    """ Create internal forwarding rule """
    ports = str(context.properties['applicationPort']).split()
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
                    "group": context.properties['instanceGroups'][0],
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
    # pylint: disable-msg=duplicate-code

    name = context.properties.get('name') or \
           context.env['name']

    deployment_name = generate_name(context.properties['uniqueString'], name)

    forwarding_rules = []
    forwarding_rule_outputs = []
    external_resources = []

    int_forwarding_rules = []
    internal_resources = []

    if context.properties['numberOfForwardingRules'] != 0:
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

    # mgmt access
    mgmt_rule_config = {
        'ports': str(context.properties['guiPortMgmt']) + ' ' + '22',
        'source': str(context.properties['restrictedSrcAddressMgmt']),
        'prefix': 'mgmtfw-',
        'network': context.properties['networkSelfLinkMgmt']
    }

    # external VIP access
    app_ext_vip_rule_config = {
        'ports': str(context.properties['applicationVipPort']),
        'source': str(context.properties['restrictedSrcAddressApp']),
        'prefix': 'appfwvip-',
        'network': context.properties['networkSelfLinkExternal'] \
            if context.properties['numberOfNics'] != 1 \
                else context.properties['networkSelfLinkMgmt']
    }

    # app server access
    app_rule_config = {
        'ports': str(context.properties['applicationPort']),
        'source': str(context.properties['restrictedSrcAddressAppInternal']),
        'prefix': 'appfwint-',
        'network': context.properties['networkSelfLinkApp'] \
            if context.properties['numberOfNics'] != 1 \
                else context.properties['networkSelfLinkMgmt']
    }

    # internal VIP access
    app_int_vip_rule_config = {
        'ports': str(context.properties['applicationPort']),
        'source': str(context.properties['restrictedSrcAddressAppInternal']),
        'prefix': 'appfwintvip-',
        'network': context.properties['networkSelfLinkInternal'] \
            if context.properties['numberOfNics'] != 1 \
                else context.properties['networkSelfLinkMgmt']
    }

    resources = [
        create_firewall_rule(context, mgmt_rule_config),
        create_firewall_rule(context, app_ext_vip_rule_config),
        create_firewall_rule(context, app_rule_config),
    ]
    if context.properties['numberOfNics'] >= 3:
        resources = resources + [create_firewall_rule(context, app_int_vip_rule_config)]

    # add external lb resources when numberOfForwardingRules not equal to 0
    resources = resources + external_resources
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

    return {
        'resources':
            resources,
        'outputs':
            outputs
    }
