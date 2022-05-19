# Copyright 2021 F5 Networks All rights reserved.
#
# Version 2.2.0.0


"""Creates full stack for POC"""
COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'


def generate_name(prefix, suffix):
    """ Generate unique name """
    return prefix + "-" + suffix

def create_access_deployment(context):
    """Create template deployment."""
    deployment = {
      'name': 'access',
      'type': '../modules/access/access.py',
      'properties': {
        'solutionType': 'failover',
        'uniqueString': context.properties['uniqueString']
      }
    }
    return [deployment]

def create_bigip_deployment(context, num_nics, instance_number):
    """ Create bigip-standalone module deployment """
    interface_config_array = []
    depends_on_array = []
    prefix = context.properties['uniqueString']
    for nics in range(num_nics):
        access_config = {}
        if nics == 0:
            net_name = context.properties['networks']['externalNetworkName']
            subnet_name = context.properties['subnets']['appSubnetName']
            interface_description = 'Interface used for external traffic'
            access_config = {
                'accessConfigs': [{ 'name': 'External NAT', 'type': 'ONE_TO_ONE_NAT' }]
            }
            network_ip = context.properties['bigIpExternalSelfIp0' + str(instance_number)]
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
            network_ip = context.properties['bigIpMgmtAddress0' + str(instance_number)]
        else:
            net_name = context.properties['networks']['internalNetworkName']
            subnet_name = context.properties['subnets']['internalSubnetName']
            interface_description = 'Interface used for internal traffic'
            if nics == 2:
                network_ip = context.properties['bigIpInternalSelfIp0' + str(instance_number)]

        net_ref = COMPUTE_URL_BASE + 'projects/' + \
                  context.env['project'] + '/global/networks/' + net_name
        sub_ref = COMPUTE_URL_BASE + 'projects/' + context.env['project'] + \
                  '/regions/' + context.properties['region'] + \
                  '/subnetworks/' + subnet_name
        interface_config = {
            'description': interface_description,
            'network': net_ref,
            'subnetwork': sub_ref,
            'networkIP': network_ip
        }
        interface_config.update(access_config)
        depends_on_array.append(net_name)
        depends_on_array.append(subnet_name)
        interface_config_array.append(interface_config)
    if instance_number == 1:
        storage_config = [{
            'name': context.properties['cfeBucket'],
            'labels': {
                'f5_cloud_failover_label': context.properties['cfeTag']
                }
            }]
    else:
        storage_config = []
    bigip_config = [{
        'name': 'bigip-failover' + str(instance_number),
        'type': '../modules/bigip-standalone/bigip_standalone.py',
        'properties': {
            'bigIpRuntimeInitConfig': context.properties['bigIpRuntimeInitConfig0' + str(instance_number)],
            'bigIpRuntimeInitPackageUrl': context.properties['bigIpRuntimeInitPackageUrl'],
            'bigIpPeerAddr': context.properties['bigIpPeerAddr'] if instance_number == 2 else None,
            'imageName': context.properties['bigIpImageName'],
            'instanceType': context.properties['bigIpInstanceType'],
            'name': 'bigip' + str(instance_number),
            'networkInterfaces': interface_config_array,
            'storageBuckets': storage_config,
            'region': context.properties['region'],
            'labels': {
                'f5_cloud_failover_label': context.properties['cfeTag']
            },
            'serviceAccounts': [
                {
                    'email': context.properties['uniqueString'] + \
                        '-admin@' + context.env['project'] + '.iam.gserviceaccount.com',
                    'scopes': [
                        'https://www.googleapis.com/auth/compute',\
                        'https://www.googleapis.com/auth/devstorage.read_write',\
                        'https://www.googleapis.com/auth/cloud-platform'
                    ]
                }
            ],
            'tags': {
                'items': [
                    generate_name(prefix, 'mgmt-fw'),
                    generate_name(prefix, 'app-vip-fw'),
                    generate_name(prefix, 'app-int-fw'),
                    generate_name(prefix, 'app-int-vip-fw'),
                    generate_name(prefix, 'ha-fw')
                ]
            },
            'targetInstances': [{
                'name': 'bigip' + str(instance_number)
            }],
            'uniqueString': context.properties['uniqueString'],
            'zone': context.properties['zone']
        },
        'metadata': {
            'dependsOn': depends_on_array
        }
    }]
    return bigip_config

def create_dag_deployment(context, num_nics):
    """ Create dag module deployment """
    prefix = context.properties['uniqueString']
    mgmt_net_name = context.properties['networks']['mgmtNetworkName']
    ext_net_name = context.properties['networks']['externalNetworkName']
    int_net_name = context.properties['networks']['internalNetworkName']
    if num_nics == 1:
        app_net_name = context.properties['networks']['mgmtNetworkName']
        int_net_name = context.properties['networks']['mgmtNetworkName']
    elif num_nics == 2:
        app_net_name = context.properties['networks']['externalNetworkName']
        int_net_name = context.properties['networks']['externalNetworkName']
    else:
        app_net_name = context.properties['networks']['externalNetworkName']
        int_net_name = context.properties['networks']['internalNetworkName']
    mgmt_net_ref = COMPUTE_URL_BASE + 'projects/' + \
                   context.env['project'] + '/global/networks/' + mgmt_net_name
    external_net_ref = COMPUTE_URL_BASE + 'projects/' + \
                       context.env['project'] + '/global/networks/' + ext_net_name
    internal_net_ref = COMPUTE_URL_BASE + 'projects/' + \
                       context.env['project'] + '/global/networks/' + int_net_name
    int_net_cidr = '10.0.' + str(num_nics - 1) + '.0/24'
    depends_on_array = []
    depends_on_array.append(mgmt_net_name)
    mgmt_port = 8443
    if num_nics > 1:
        depends_on_array.append(ext_net_name)
        mgmt_port = 443
    if num_nics > 2:
        depends_on_array.append(int_net_name)
    if num_nics > 3:
        depends_on_array.append(app_net_name)
    target_instance_name = generate_name(prefix, 'bigip1-ti')
    target_instance_name2 = generate_name(prefix, 'bigip2-ti')
    depends_on_array.append(target_instance_name)
    depends_on_array.append(target_instance_name2)
    dag_configuration = [{
      'name': 'dag',
      'type': '../modules/dag/dag.py',
      'properties': {
            'firewalls' : [
                {
                    'allowed': [
                        {
                            'IPProtocol': 'TCP',
                            'ports': [ 22, mgmt_port, 443 ]
                        }
                    ],
                    'description': 'Allow ssh and ' + str(mgmt_port) + ' to management',
                    'name': context.properties['uniqueString'] + '-mgmt-fw',
                    'network': mgmt_net_ref,
                    'sourceRanges': [ 
                        context.properties['restrictedSrcAddressMgmt'], 
                        context.properties['bigIpMgmtAddress01'], 
                        context.properties['bigIpMgmtAddress02'] 
                    ],
                    'targetTags': [ generate_name(prefix, 'mgmt-fw') ]
                },
                {
                    'allowed': [
                        {
                            'IPProtocol': 'TCP',
                            'ports': [ 80, 443 ]
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
                },
                {
                    'allowed': [
                        {
                            'IPProtocol': 'TCP',
                            'ports': [ 4353, 443 ]
                        },
                        {   'IPProtocol': 'UDP',
                            'ports': [ 1026 ]
                        }
                    ],
                    'description': 'Allow HA traffic from BIGIPs',
                    'name': context.properties['uniqueString'] + '-ha-fw',
                    'network': external_net_ref,
                    'sourceTags': [ generate_name(prefix, 'ha-fw') ],
                    'targetTags': [ generate_name(prefix, 'ha-fw') ]
                }
            ],
            'forwardingRules': [
                {
                    'name': context.properties['uniqueString'] + '-fwrule1',
                    'region': context.properties['region'],
                    'IPProtocol': 'TCP',
                    'target': '$(ref.' + target_instance_name + '.selfLink)',
                    'loadBalancingScheme': 'EXTERNAL',
                    'description': 'f5_cloud_failover_labels={\"f5_cloud_failover_label\":\"' + context.properties['cfeTag'] + '\",\"f5_target_instance_pair\":\"' + target_instance_name + ',' + target_instance_name2 + '\"}'
                },
                {
                    'name': context.properties['uniqueString'] + '-fwrule2',
                    'region': context.properties['region'],
                    'IPProtocol': 'TCP',
                    'target': '$(ref.' + target_instance_name2 + '.selfLink)',
                    'loadBalancingScheme': 'EXTERNAL',
                    'description': 'f5_cloud_failover_labels={\"f5_cloud_failover_label\":\"' + context.properties['cfeTag'] + '\",\"f5_target_instance_pair\":\"' + target_instance_name + ',' + target_instance_name2 + '\"}'
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

    num_nics = 3
    name = context.properties.get('name') or \
           context.env['name']
    prefix = context.properties['uniqueString']

    deployment_name = generate_name(context.properties['uniqueString'], name)
    bigip_instance_name = generate_name(prefix, 'bigip1')
    bigip_instance_name2 = generate_name(prefix, 'bigip2')
    fw_rule_name = generate_name(prefix, 'fwrule1')

    resources = create_access_deployment(context) + \
        create_bigip_deployment(context, num_nics, 1) + \
        create_bigip_deployment(context, num_nics, 2) + \
        create_dag_deployment(context, num_nics)
    outputs = []
    mgmt_nic_index = '0' if num_nics == 1 else '1'
    mgmt_port = '8443' if num_nics == 1 else '443'

    if context.properties['provisionPublicIp']:
        outputs = outputs + [
            {
                'name': 'bigIpManagementPublicIp1',
                'value': '$(ref.' + bigip_instance_name + '.networkInterfaces[' + mgmt_nic_index + '].accessConfigs[0].natIP)'
            },
            {
                'name': 'bigIpManagementPublicIp2',
                'value': '$(ref.' + bigip_instance_name2 + '.networkInterfaces[' + mgmt_nic_index + '].accessConfigs[0].natIP)'
            },
            {
                'name': 'bigIpManagementPublicUrl1',
                'value': 'https://' + '$(ref.' + bigip_instance_name + '.networkInterfaces[' + mgmt_nic_index + '].accessConfigs[0].natIP)' + ':' + mgmt_port
            },
            {
                'name': 'bigIpManagementPublicUrl2',
                'value': 'https://' + '$(ref.' + bigip_instance_name2 + '.networkInterfaces[' + mgmt_nic_index + '].accessConfigs[0].natIP)' + ':' + mgmt_port
            },
            {
                'name': 'bigIpManagementPublicSsh1',
                'value': 'ssh admin@' + '$(ref.' + bigip_instance_name + '.networkInterfaces[' + mgmt_nic_index + '].accessConfigs[0].natIP)'
            },
            {
                'name': 'bigIpManagementPublicSsh2',
                'value': 'ssh admin@' + '$(ref.' + bigip_instance_name2 + '.networkInterfaces[' + mgmt_nic_index + '].accessConfigs[0].natIP)'
            }
        ]

    outputs = outputs + [
        {
            'name': 'deploymentName',
            'value': deployment_name
        },
        {
            'name': 'bigIpInstanceId1',
            'value': '$(ref.' + bigip_instance_name + '.id)'
        },
        {
            'name': 'bigIpInstanceId2',
            'value': '$(ref.' + bigip_instance_name2 + '.id)'
        },
        {
            'name': 'bigIpInstanceName1',
            'value': bigip_instance_name
        },
        {
            'name': 'bigIpInstanceName2',
            'value': bigip_instance_name2
        },
        {
            'name': 'bigIpManagementPrivateIp1',
            'value': '$(ref.' + bigip_instance_name + '.networkInterfaces[' + mgmt_nic_index + '].networkIP)'
        },
        {
            'name': 'bigIpManagementPrivateIp2',
            'value': '$(ref.' + bigip_instance_name2 + '.networkInterfaces[' + mgmt_nic_index + '].networkIP)'
        },
        {
            'name': 'bigIpManagementPrivateUrl1',
            'value': 'http://' + '$(ref.' + bigip_instance_name + '.networkInterfaces[' + mgmt_nic_index + '].networkIP)' + ':' + mgmt_port
        },
        {
            'name': 'bigIpManagementPrivateUrl2',
            'value': 'http://' + '$(ref.' + bigip_instance_name2 + '.networkInterfaces[' + mgmt_nic_index + '].networkIP)' + ':' + mgmt_port
        },
        {
            'name': 'bigIpUsername',
            'value': 'admin'
        },
        {
            'name': 'vip1PrivateIp1',
            'value': '$(ref.' + bigip_instance_name + '.networkInterfaces[0].networkIP)'
        },
        {
            'name': 'vip1PrivateIp2',
            'value': '$(ref.' + bigip_instance_name2 + '.networkInterfaces[0].networkIP)'
        },
        {
            'name': 'vip1PrivateUrlHttp1',
            'value': 'http://' + '$(ref.' + bigip_instance_name + '.networkInterfaces[0].networkIP)'
        },
        {
            'name': 'vip1PrivateUrlHttp2',
            'value': 'http://' + '$(ref.' + bigip_instance_name2 + '.networkInterfaces[0].networkIP)'
        },
        {
            'name': 'vip1PrivateUrlHttps1',
            'value': 'https://' + '$(ref.' + bigip_instance_name + '.networkInterfaces[0].networkIP)'
        },
        {
            'name': 'vip1PrivateUrlHttps2',
            'value': 'https://' + '$(ref.' + bigip_instance_name2 + '.networkInterfaces[0].networkIP)'
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
