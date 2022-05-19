# Copyright 2021 F5 Networks All rights reserved.
#
# Version 2.2.0.0


"""Creates full stack for POC"""
COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'


def generate_name(prefix, suffix):
    """ Generate unique name """
    return prefix + "-" + suffix

def create_network_deployment(context, num_nics):
    """ Create network module deployment """
    network_config = {}
    network_config_array = []
    for nics in range(num_nics):
        if nics == 0:
            net_name = 'mgmt'
            subnet_name = 'mgmt'
            subnet_description = 'Subnetwork used for management traffic'
        elif num_nics != 1 and nics == 1:
            net_name = 'external'
            subnet_name = 'external'
            subnet_description = 'Subnetwork used for external traffic'
        else:
            net_name = 'internal' + str(nics)
            subnet_name = 'internal' + str(nics)
            subnet_description = 'Subnetwork used for internal traffic'
        subnet_config = [{
            'description': subnet_description,
            'name': subnet_name,
            'region': context.properties['region'],
            'ipCidrRange': '10.0.' + str(nics) + '.0/24'
        }]
        if nics + 1 == num_nics:
            app_subnet_config = {
                'description': 'Subnetwork used for POC application.',
                'name': 'app',
                'region': context.properties['region'],
                'ipCidrRange': '10.0.' + str(nics + 1) + '.0/24'
            }
            subnet_config.append(app_subnet_config)
        network_config = {
            'name': 'network' + str(nics),
            'type': '../modules/network/network.py',
            'properties': {
                'name': net_name,
                'provisionPublicIp': context.properties['provisionPublicIp'],
                'region': context.properties['region'],
                'uniqueString': context.properties['uniqueString'],
                'subnets': subnet_config
            }
        }
        network_config_array.append(network_config)
    return network_config_array

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
            net_name = generate_name(prefix, 'external-network')
            subnet_name = generate_name(prefix, 'external-subnet')
            interface_description = 'Interface used for external traffic'
            access_config = {
                'accessConfigs': [{ 'name': 'External NAT', 'type': 'ONE_TO_ONE_NAT' }]
            }
            network_ip = context.properties['bigIpExternalSelfIp0' + str(instance_number)]
        elif nics == 1:
            net_name = generate_name(prefix, 'mgmt-network')
            subnet_name = generate_name(prefix, 'mgmt-subnet')
            interface_description = 'Interface used for management traffic'
            if context.properties['provisionPublicIp']:
                access_config = {
                    'accessConfigs': [{ 'name': 'Management NAT', 'type': 'ONE_TO_ONE_NAT' }]
                }
            else:
                access_config = {'accessConfigs': []}
            network_ip = context.properties['bigIpMgmtAddress0' + str(instance_number)]
        else:
            net_name = generate_name(prefix, 'internal' + str(nics) + '-network')
            subnet_name = generate_name(prefix, 'internal' + str(nics) + '-subnet')
            interface_description = 'Interface used for internal traffic'
            if nics == 2:
                network_ip = context.properties['bigIpInternalSelfIp0' + str(instance_number)]
        interface_config = {
            'description': interface_description,
            'network': '$(ref.' + net_name + '.selfLink)',
            'subnetwork': '$(ref.' + subnet_name + '.selfLink)',
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

def create_application_deployment(context, num_nics):
    """ Create application module deployment """
    prefix = context.properties['uniqueString']
    subnet_name = generate_name(prefix, 'app-subnet')
    if num_nics == 1:
        net_name = generate_name(prefix, 'mgmt-network')
    elif num_nics == 2:
        net_name = generate_name(prefix, 'external-network')
    else:
        net_name = generate_name(prefix, 'internal' + \
            str(num_nics - 1) + '-network')
    depends_on_array = []
    depends_on_array.append(net_name)
    depends_on_array.append(subnet_name)
    application_config = [{
      'name': 'application',
      'type': '../modules/application/application.py',
      'properties': {
        'appContainerName': context.properties['appContainerName'],
        'application': context.properties['application'],
        'cost': context.properties['cost'],
        'environment': context.properties['environment'],
        'group': context.properties['group'],
        'instanceType': 'n1-standard-1',
        'instances': [{
            'description': 'F5 demo application',
            'labels': {
                'failovergroup': context.properties['uniqueString']
            },
            'networkInterfaces': [{
                'accessConfigs': [{
                    'name': 'External NAT',
                    'type': 'ONE_TO_ONE_NAT'
                }],
                'description': 'Interface used for external traffic',
                'network': '$(ref.' + net_name + '.selfLink)',
                'subnetwork': '$(ref.' + subnet_name + '.selfLink)'
            }],
            'zone': context.properties['zone']
        }],
        'uniqueString': context.properties['uniqueString'],
      },
      'metadata': {
        'dependsOn': depends_on_array
      }
    }]
    return application_config

def create_bastion_deployment(context):
    """ Create template deployment """
    prefix = context.properties['uniqueString']
    net_name = generate_name(prefix, 'mgmt-network')
    subnet_name = generate_name(prefix, 'mgmt-subnet')
    depends_on_array = []
    depends_on_array.append(net_name)
    depends_on_array.append(subnet_name)
    bastion_config = {
        'name': 'bastion',
        'type': '../modules/bastion/bastion.py',
        'properties': {
            'application': context.properties['application'],
            'cost': context.properties['cost'],
            'environment': context.properties['environment'],
            'group': context.properties['group'],
            'owner': context.properties['owner'],
            'instanceType': 'n1-standard-1',
            'instances': [{
                'description': 'My bastion host',
                'networkInterfaces': [{
                    'accessConfigs': [{
                        'name': 'External NAT',
                        'type': 'ONE_TO_ONE_NAT'
                    }],
                    'description': 'Interface used for external traffic',
                    'network': '$(ref.' + net_name + '.selfLink)',
                    'subnetwork': '$(ref.' + subnet_name + '.selfLink)'
                }],
                'zone': context.properties['zone']
            }],
            'uniqueString': context.properties['uniqueString']
        },
        'metadata': {
            'dependsOn': depends_on_array
        }
    }
    return bastion_config

def create_dag_deployment(context, num_nics):
    """ Create dag module deployment """
    prefix = context.properties['uniqueString']
    mgmt_net_name = generate_name(prefix, 'mgmt-network')
    ext_net_name = generate_name(prefix, 'external-network')
    int_net_name = generate_name(prefix, 'internal2-network')
    if num_nics == 1:
        app_net_name = generate_name(prefix, 'mgmt-network')
        int_net_name = generate_name(prefix, 'mgmt-network')
    elif num_nics == 2:
        app_net_name = generate_name(prefix, 'external-network')
        int_net_name = generate_name(prefix, 'external-network')
    else:
        app_net_name = generate_name(prefix, 'external-network')
        int_net_name = generate_name(prefix, 'internal' + \
            str(num_nics - 1) + '-network')
    int_net_cidr = '10.0.' + str(num_nics - 1) + '.0/24'
    mgmt_port = 8443
    bastion_instance_name = generate_name(prefix, 'bastion')
    firewalls_config = [
        {
            'allowed': [
                {
                    'IPProtocol': 'TCP',
                    'ports': [ 22, mgmt_port, 443 ]
                }
            ],
            'description': 'Allow ssh and ' + str(mgmt_port) + ' to management',
            'name': context.properties['uniqueString'] + '-mgmt-fw',
            'network': '$(ref.' + mgmt_net_name + '.selfLink)',
            'sourceRanges': [ 
                context.properties['restrictedSrcAddressMgmt'] if context.properties['provisionPublicIp'] else '$(ref.' + bastion_instance_name + '.networkInterfaces[0].networkIP)', 
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
            'network': '$(ref.' + int_net_name + '.selfLink)',
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
            'network': '$(ref.' + app_net_name + '.selfLink)',
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
            'network': '$(ref.' + ext_net_name + '.selfLink)',
            'sourceTags': [ generate_name(prefix, 'ha-fw') ],
            'targetTags': [ generate_name(prefix, 'ha-fw') ]
        }
    ]
    bastion_firewall_config = {
        'allowed': [
            {
                'IPProtocol': 'TCP',
                'ports': [ 22, mgmt_port, 443 ]
            }
        ],
        'description': 'Allow ssh and ' + str(mgmt_port) + ' to bastion',
        'name': context.properties['uniqueString'] + '-bastion-fw',
        'network': '$(ref.' + mgmt_net_name + '.selfLink)',
        'sourceRanges': [ 
            context.properties['restrictedSrcAddressMgmt']
        ],
        'targetTags': [ generate_name(prefix, 'bastion-fw') ]
    }
    if not context.properties['provisionPublicIp']:
        firewalls_config.append(bastion_firewall_config)
    depends_on_array = []
    depends_on_array.append(mgmt_net_name)
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
            'firewalls' : firewalls_config,
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
    application_instance_name = generate_name(prefix, 'application')
    bastion_instance_name = generate_name(prefix, 'bastion')
    bigip_instance_name = generate_name(prefix, 'bigip1')
    bigip_instance_name2 = generate_name(prefix, 'bigip2')
    fw_rule_name = generate_name(prefix, 'fwrule1')
    mgmt_net_name = generate_name(prefix, 'mgmt-network')
    ext_net_name = generate_name(prefix, 'external-network')
    int_net_name = generate_name(prefix, 'internal' + \
        str(num_nics - 1) + '-network')

    resources = create_network_deployment(context, num_nics) + \
        create_access_deployment(context) + \
        create_bigip_deployment(context, num_nics, 1) + \
        create_bigip_deployment(context, num_nics, 2) + \
        create_application_deployment(context, num_nics) + \
        create_dag_deployment(context, num_nics)
    outputs = []
    mgmt_nic_index = '0' if num_nics == 1 else '1'
    mgmt_port = '8443' if num_nics == 1 else '443'

    if not context.properties['provisionPublicIp']:
        resources = resources + [create_bastion_deployment(context)]
        outputs = outputs + [
            {
                'name': 'bastionInstanceId',
                'value': '$(ref.' + bastion_instance_name + '.id)'
            },
            {
                'name': 'bastionPublicIp',
                'value': '$(ref.' + bastion_instance_name + '.networkInterfaces[0].accessConfigs[0].natIP)'
            },
            {
                'name': 'bastionPublicSsh',
                'value': 'ssh ubuntu@' + '$(ref.' + bastion_instance_name + '.networkInterfaces[0].accessConfigs[0].natIP)'
            }
        ]
    else:
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

    if num_nics == 2:
        outputs = outputs + [
            {
                'name': 'networkName1',
                'value': ext_net_name
            },
            {
                'name': 'networkSelfLink1',
                'value': '$(ref.' + ext_net_name + '.selfLink)'
            }
        ]

    if num_nics == 3:
        outputs = outputs + [
            {
                'name': 'networkName2',
                'value': int_net_name
            },
            {
                'name': 'networkSelfLink2',
                'value': '$(ref.' + int_net_name + '.selfLink)'
            }
        ]

    outputs = outputs + [
        {
            'name': 'deploymentName',
            'value': deployment_name
        },
        {
            'name': 'appPrivateIp',
            'value': '$(ref.' + application_instance_name + '.networkInterfaces[0].networkIP)'
        },
        {
            'name': 'appPublicIp',
            'value': '$(ref.' + application_instance_name + '.networkInterfaces[0].accessConfigs[0].natIP)'
        },
        {
            'name': 'appUsername',
            'value': 'ubuntu'
        },
        {
            'name': 'appInstanceName',
            'value': application_instance_name
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
        },
        {
            'name': 'networkName0',
            'value': mgmt_net_name
        },
        {
            'name': 'networkSelfLink0',
            'value': '$(ref.' + mgmt_net_name + '.selfLink)'
        }
    ]

    return {
        'resources':
            resources,
        'outputs':
            outputs
    }
