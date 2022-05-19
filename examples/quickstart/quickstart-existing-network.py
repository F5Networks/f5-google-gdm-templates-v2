# Copyright 2021 F5 Networks All rights reserved.
#
# Version 2.2.0.0


"""Creates full stack for POC"""
COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'


def generate_name(prefix, suffix):
    """ Generate unique name """
    return prefix + "-" + suffix

def create_bigip_deployment(context):
    """ Create bigip-standalone module deployment """
    interface_config_array = []
    depends_on_array = []
    prefix = context.properties['uniqueString']
    for nics in range(context.properties['numNics']):
        access_config = {}
        if context.properties['numNics'] != 1 and nics == 0:
            net_name = context.properties['networks']['externalNetworkName']
            subnet_name = context.properties['subnets']['appSubnetName']
            interface_description = 'Interface used for external traffic'
            access_config = {
                'accessConfigs': [{ 'name': 'External NAT', 'type': 'ONE_TO_ONE_NAT' }]
            }
        elif nics == 0:
            net_name = context.properties['networks']['mgmtNetworkName']
            subnet_name = context.properties['subnets']['mgmtSubnetName']
            interface_description = 'Interface used for management traffic'
            if context.properties['provisionPublicIp']:
                access_config = {
                    'accessConfigs': [{ 'name': 'Management NAT', 'type': 'ONE_TO_ONE_NAT' }]
                }
            else:
                access_config = {'accessConfigs': []}
        elif nics == 1:
            net_name = context.properties['networks']['mgmtNetworkName']
            subnet_name = context.properties['subnets']['mgmtSubnetName']
            interface_description = 'Interface used for management traffic'
            if context.properties['provisionPublicIp']:
                access_config = {
                    'accessConfigs': [{ 'name': 'Management NAT', 'type': 'ONE_TO_ONE_NAT' }]
                }
            else:
                access_config = {'accessConfigs': []}
        else:
            net_name = context.properties['networks']['internalNetworkName']
            subnet_name = context.properties['subnets']['internalSubnetName']
            interface_description = 'Interface used for internal traffic'
        net_ref = COMPUTE_URL_BASE + 'projects/' + \
                  context.env['project'] + '/global/networks/' + net_name
        sub_ref = COMPUTE_URL_BASE + 'projects/' + context.env['project'] + \
                  '/regions/' + context.properties['region'] + \
                  '/subnetworks/' + subnet_name
        interface_config = {
            'description': interface_description,
            'network': net_ref,
            'subnetwork': sub_ref
        }
        interface_config.update(access_config)
        depends_on_array.append(net_name)
        depends_on_array.append(subnet_name)
        interface_config_array.append(interface_config)
    bigip_config = [{
        'name': 'bigip-standalone',
        'type': '../modules/bigip-standalone/bigip_standalone.py',
        'properties': {
            'bigIpRuntimeInitConfig': context.properties['bigIpRuntimeInitConfig'],
            'bigIpRuntimeInitPackageUrl': context.properties['bigIpRuntimeInitPackageUrl'],
            'imageName': context.properties['bigIpImageName'],
            'instanceType': context.properties['bigIpInstanceType'],
            'name': 'bigip1',
            'networkInterfaces': interface_config_array,
            'region': context.properties['region'],
            'tags': {
                'items': [
                    generate_name(prefix, 'mgmt-fw'),
                    generate_name(prefix, 'app-vip-fw'),
                    generate_name(prefix, 'app-int-fw'),
                    generate_name(prefix, 'app-int-vip-fw')
                ]
            },
            'targetInstances': [{
                'name': 'bigip'
            }],
            'uniqueString': context.properties['uniqueString'],
            'zone': context.properties['zone']
        },
        'metadata': {
            'dependsOn': depends_on_array
        }
    }]
    return bigip_config

def create_dag_deployment(context):
    """ Create dag module deployment """
    prefix = context.properties['uniqueString']
    mgmt_net_name = context.properties['networks']['mgmtNetworkName']
    ext_net_name = context.properties['networks']['externalNetworkName']
    int_net_name = context.properties['networks']['internalNetworkName']
    if context.properties['numNics'] == 1:
        ext_net_name = context.properties['networks']['mgmtNetworkName']
        int_net_name = context.properties['networks']['mgmtNetworkName']
    elif context.properties['numNics'] == 2:
        ext_net_name = context.properties['networks']['externalNetworkName']
        int_net_name = context.properties['networks']['externalNetworkName']
    else:
        ext_net_name = context.properties['networks']['externalNetworkName']
        int_net_name = context.properties['networks']['internalNetworkName']
    mgmt_net_ref = COMPUTE_URL_BASE + 'projects/' + \
                   context.env['project'] + '/global/networks/' + mgmt_net_name
    external_net_ref = COMPUTE_URL_BASE + 'projects/' + \
                       context.env['project'] + '/global/networks/' + ext_net_name
    internal_net_ref = COMPUTE_URL_BASE + 'projects/' + \
                       context.env['project'] + '/global/networks/' + int_net_name
    int_net_cidr = '10.0.' + str(context.properties['numNics'] - 1) + '.0/24'
    depends_on_array = []
    depends_on_array.append(mgmt_net_name)
    mgmt_port = 8443
    if context.properties['numNics'] > 1:
        depends_on_array.append(ext_net_name)
        mgmt_port = 443
    if context.properties['numNics'] > 2:
        depends_on_array.append(int_net_name)
    if context.properties['numNics'] > 3:
        depends_on_array.append(ext_net_name)
    target_instance_name = generate_name(prefix, 'bigip-ti')
    depends_on_array.append(target_instance_name)
    dag_configuration = [{
      'name': 'dag',
      'type': '../modules/dag/dag.py',
      'properties': {
            'firewalls' : [
                {
                    'allowed': [
                        {
                            'IPProtocol': 'TCP',
                            'ports': [ 22, mgmt_port , 443 ]
                        }
                    ],
                    'description': 'Allow ssh and ' + str(mgmt_port) + ' to management',
                    'name': context.properties['uniqueString'] + '-mgmt-fw',
                    'network': mgmt_net_ref,
                    'sourceRanges': [ context.properties['restrictedSrcAddressMgmt'] ],
                    'targetTags': [ generate_name(prefix, 'mgmt-fw') ]
                },
                {
                    'allowed': [
                        {
                            'IPProtocol': 'TCP',
                            'ports': [ 80 , 443 ]
                        }
                    ],
                    'description': 'Allow web traffic to internal app network',
                    'name': context.properties['uniqueString'] + '-app-int-fw',
                    'network': internal_net_ref,
                    'sourceRanges': [ int_net_cidr ],
                    'targetTags': [
                        generate_name(prefix, 'app-int-fw'),
                        generate_name(prefix, 'app-int-vip-fw')
                    ]
                },
                {
                    'allowed': [
                        {
                            'IPProtocol': 'TCP',
                            'ports': [ 80, 443 ]
                        }
                    ],
                    'description': 'Allow web traffic to public network',
                    'name': context.properties['uniqueString'] + '-app-vip-fw',
                    'network': external_net_ref,
                    'sourceRanges': [ context.properties['restrictedSrcAddressApp'] ],
                    'targetTags': [ generate_name(prefix, 'app-vip-fw') ]
                }
            ],
            'forwardingRules': [
                {
                    'name': context.properties['uniqueString'] + '-fwrule1',
                    'region': context.properties['region'],
                    'IPProtocol': 'TCP',
                    'target': '$(ref.' + target_instance_name + '.selfLink)',
                    'loadBalancingScheme': 'EXTERNAL'
                }
            ],
            'healthChecks': [
                {
                    'checkIntervalSec': 5,
                    'description': 'my tcp healthcheck',
                    'name': context.properties['uniqueString'] + '-tcp-healthcheck',
                    'tcpHealthCheck': {
                        'port': 44000
                    },
                    'timeoutSec': 5,
                    'type': 'TCP'
                },
                {
                    'checkIntervalSec': 5,
                    'description': 'my http healthcheck',
                    'name': context.properties['uniqueString'] + '-http-healthcheck',
                    'httpHealthCheck': {
                        'port': 80
                    },
                    'timeoutSec': 5,
                    'type': 'HTTP'
                },
                {
                    'checkIntervalSec': 5,
                    'description': 'my https healthcheck',
                    'name': context.properties['uniqueString'] + '-https-healthcheck',
                    'httpsHealthCheck': {
                        'port': 443
                    },
                    'timeoutSec': 5,
                    'type': 'HTTPS'
                }
            ],
            'uniqueString': context.properties['uniqueString']
        },
      'metadata': {
        'dependsOn': depends_on_array
      }
    }]
    return dag_configuration

def generate_config(context):
    """ Entry point for the deployment resources. """

    name = context.properties.get('name') or \
           context.env['name']
    prefix = context.properties['uniqueString']

    deployment_name = generate_name(context.properties['uniqueString'], name)
    bigip_instance_name= generate_name(prefix, 'bigip1')
    fw_rule_name = generate_name(prefix, 'fwrule1')

    resources = create_bigip_deployment(context) + create_dag_deployment(context)
    outputs = []
    mgmt_nic_index = '0' if context.properties['numNics'] == 1 else '1'
    mgmt_port = '8443' if context.properties['numNics'] == 1 else '443'

    if context.properties['provisionPublicIp']:
        outputs = outputs + [
            {
                'name': 'bigIpManagementPublicIp',
                'value': '$(ref.' + bigip_instance_name + '.networkInterfaces[' + mgmt_nic_index + '].accessConfigs[0].natIP)'
            },
            {
                'name': 'bigIpManagementPublicUrl',
                'value': 'https://' + '$(ref.' + bigip_instance_name + '.networkInterfaces[' + mgmt_nic_index + '].accessConfigs[0].natIP)' + ':' + mgmt_port
            },
            {
                'name': 'bigIpManagementPublicSsh',
                'value': 'ssh quickstart@' + '$(ref.' + bigip_instance_name + '.networkInterfaces[' + mgmt_nic_index + '].accessConfigs[0].natIP)'
            }
        ]

    outputs = outputs + [
        {
            'name': 'deploymentName',
            'value': deployment_name
        },
        {
            'name': 'bigIpInstanceId',
            'value': '$(ref.' + bigip_instance_name + '.id)'
        },
        {
            'name': 'bigIpInstanceName',
            'value': bigip_instance_name
        },
        {
            'name': 'bigIpManagementPrivateIp',
            'value': '$(ref.' + bigip_instance_name + '.networkInterfaces[' + mgmt_nic_index + '].networkIP)'
        },
        {
            'name': 'bigIpManagementPrivateUrl',
            'value': 'http://' + '$(ref.' + bigip_instance_name + '.networkInterfaces[' + mgmt_nic_index + '].networkIP)' + ':' + mgmt_port
        },
        {
            'name': 'bigIpUsername',
            'value': 'quickstart'
        },
        {
            'name': 'vip1PrivateIp',
            'value': '$(ref.' + bigip_instance_name + '.networkInterfaces[0].networkIP)'
        },
        {
            'name': 'vip1PrivateUrlHttp',
            'value': 'http://' + '$(ref.' + bigip_instance_name + '.networkInterfaces[0].networkIP)'
        },
        {
            'name': 'vip1PrivateUrlHttps',
            'value': 'https://' + '$(ref.' + bigip_instance_name + '.networkInterfaces[0].networkIP)'
        },
        {
            'name': 'vip1PublicIp',
            'value': '$(ref.' + fw_rule_name + '.IPAddress)'
        },
        {
            'name': 'vip1PublicUrlHttp',
            'value': 'http://' + '$(ref.' + fw_rule_name + '.IPAddress)'
        },
        {
            'name': 'vip1PublicUrlHttps',
            'value': 'https://' + '$(ref.' + fw_rule_name + '.IPAddress)'
        }
    ]

    return {
        'resources':
            resources,
        'outputs':
            outputs
    }
