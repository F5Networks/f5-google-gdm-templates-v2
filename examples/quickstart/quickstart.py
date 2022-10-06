# Copyright 2021 F5 Networks All rights reserved.
#
# Version 2.5.0.0


"""Creates full stack for POC"""
COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'


def generate_name(prefix, suffix):
    """ Generate unique name """
    return prefix + "-" + suffix

def create_network_deployment(context):
    """ Create network module deployment """
    network_config = {}
    network_config_array = []
    for nics in range(context.properties['numNics']):
        if nics == 0:
            net_name = 'mgmt-network'
            subnet_name = 'mgmt-subnet'
            subnet_description = 'Subnetwork used for management traffic'
        elif context.properties['numNics'] != 1 and nics == 1:
            net_name = 'ext-network'
            subnet_name = 'ext-subnet'
            subnet_description = 'Subnetwork used for external traffic'
        else:
            net_name = 'int-network-0' + str(nics)
            subnet_name = 'int-subnet-0' + str(nics)
            subnet_description = 'Subnetwork used for internal traffic'
        subnet_config = [{
            'description': subnet_description,
            'name': subnet_name,
            'region': context.properties['region'],
            'ipCidrRange': '10.0.' + str(nics) + '.0/24'
        }]
        if nics + 1 == context.properties['numNics']:
            app_subnet_config = {
                'description': 'Subnetwork used for POC application.',
                'name': 'app-subnet',
                'region': context.properties['region'],
                'ipCidrRange': '10.0.' + str(nics + 1) + '.0/24'
            }
            subnet_config.append(app_subnet_config)
        network_config = {
            'name': 'network-0' + str(nics),
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

def create_bigip_deployment(context):
    """ Create bigip-standalone module deployment """
    interface_config_array = []
    depends_on_array = []
    prefix = context.properties['uniqueString']
    for nics in range(context.properties['numNics']):
        access_config = {}
        if context.properties['numNics'] != 1 and nics == 0:
            net_name = generate_name(prefix, 'ext-network')
            subnet_name = generate_name(prefix, 'ext-subnet')
            interface_description = 'Interface used for external traffic'
            access_config = {
                'accessConfigs': [{ 'name': 'External NAT', 'type': 'ONE_TO_ONE_NAT' }]
            }
        elif nics == 0:
            net_name = generate_name(prefix, 'mgmt-network')
            subnet_name = generate_name(prefix, 'mgmt-subnet')
            interface_description = 'Interface used for management traffic'
            if context.properties['provisionPublicIp']:
                access_config = {
                    'accessConfigs': [{ 'name': 'Management NAT', 'type': 'ONE_TO_ONE_NAT' }]
                }
            else:
                access_config = {'accessConfigs': []}
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
        else:
            net_name = generate_name(prefix, 'int-network-0' + str(nics))
            subnet_name = generate_name(prefix, 'int-subnet-0' + str(nics))
            interface_description = 'Interface used for internal traffic'
        interface_config = {
            'description': interface_description,
            'network': '$(ref.' + net_name + '.selfLink)',
            'subnetwork': '$(ref.' + subnet_name + '.selfLink)'
        }
        interface_config.update(access_config)
        depends_on_array.append(net_name)
        depends_on_array.append(subnet_name)
        interface_config_array.append(interface_config)

    # Populate Metadata Tags
    additionalMetadataTags = {}

    # Populate Example VIPs
    public_ip_name = generate_name(prefix, 'public-ip-01')
    depends_on_array.append(public_ip_name)
    additionalMetadataTags.update({'service-address-01-public-ip': '$(ref.' + public_ip_name + '.address)'})

    allow_usage_analytics = context.properties['allowUsageAnalytics'] if \
        'allowUsageAnalytics' in context.properties else True
    custom_image_id = context.properties['bigIpCustomImageId'] if \
        'bigIpCustomImageId' in context.properties else ''
    hostname = context.properties['bigIpHostname'] if \
        'bigIpHostname' in context.properties else 'bigip01.local'
    license_key = context.properties['bigIpLicenseKey'] if \
        'bigIpLicenseKey' in context.properties else ''

    bigip_config = [{
        'name': 'bigip-quickstart',
        'type': '../modules/bigip-standalone/bigip_standalone.py',
        'properties': {
            'additionalMetadataTags': additionalMetadataTags,
            'allowUsageAnalytics': allow_usage_analytics,
            'bigIpRuntimeInitConfig': context.properties['bigIpRuntimeInitConfig'],
            'bigIpRuntimeInitPackageUrl': context.properties['bigIpRuntimeInitPackageUrl'],
            'customImageId': custom_image_id,
            'hostname': hostname,
            'imageName': context.properties['bigIpImageName'],
            'instanceType': context.properties['bigIpInstanceType'],
            'licenseKey': license_key,
            'name': 'bigip-vm-01',
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
                'name': 'bigip-vm-01'
            }],
            'uniqueString': context.properties['uniqueString'],
            'zone': context.properties['zone']
        },
        'metadata': {
            'dependsOn': depends_on_array
        }
    }]

    if 'bigIpServiceAccountEmail' in context.properties:
        bigip_config[0]['properties']['serviceAccounts'] = [
            {
                'email': context.properties['bigIpServiceAccountEmail'],
                'scopes': [
                    'https://www.googleapis.com/auth/compute',\
                    'https://www.googleapis.com/auth/devstorage.read_write',\
                    'https://www.googleapis.com/auth/cloud-platform'
                ]
            }
        ]

    return bigip_config

def create_application_deployment(context):
    """ Create application module deployment """
    prefix = context.properties['uniqueString']
    subnet_name = generate_name(prefix, 'app-subnet')
    if context.properties['numNics'] == 1:
        net_name = generate_name(prefix, 'mgmt-network')
    elif context.properties['numNics'] == 2:
        net_name = generate_name(prefix, 'ext-network')
    else:
        net_name = generate_name(prefix, 'int-network-0' + \
            str(context.properties['numNics'] - 1))
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
            'name': 'application-vm-01',
            'description': 'F5 demo application',
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
                'name': 'bastion-vm-01',
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

def create_dag_deployment(context):
    """ Create dag module deployment """
    prefix = context.properties['uniqueString']
    mgmt_net_name = generate_name(prefix, 'mgmt-network')
    ext_net_name = generate_name(prefix, 'ext-network')
    int_net_name = generate_name(prefix, 'int-network-02')
    if context.properties['numNics'] == 1:
        app_net_name = generate_name(prefix, 'mgmt-network')
        int_net_name = generate_name(prefix, 'mgmt-network')
    elif context.properties['numNics'] == 2:
        app_net_name = generate_name(prefix, 'ext-network')
        int_net_name = generate_name(prefix, 'ext-network')
    else:
        app_net_name = generate_name(prefix, 'ext-network')
        int_net_name = generate_name(prefix, 'int-network-0' + \
            str(context.properties['numNics'] - 1))
    int_net_cidr = '10.0.' + str(context.properties['numNics'] - 1) + '.0/24'
    mgmt_port = 8443
    bastion_instance_name = generate_name(prefix, 'bastion-vm-01')
    firewalls_config = [
        {
            'allowed': [
                {
                    'IPProtocol': 'TCP',
                    'ports': [ 22, mgmt_port , 443 ]
                }
            ],
            'description': 'Allow ssh and ' + str(mgmt_port) + ' to management',
            'name': context.properties['uniqueString'] + '-mgmt-fw',
            'network': '$(ref.' + mgmt_net_name + '.selfLink)',
            'sourceRanges': [ context.properties['restrictedSrcAddressMgmt'] if context.properties['provisionPublicIp'] else '$(ref.' + bastion_instance_name + '.networkInterfaces[0].networkIP)' ],
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
    if context.properties['numNics'] > 1:
        depends_on_array.append(ext_net_name)
        mgmt_port = 443
    if context.properties['numNics'] > 2:
        depends_on_array.append(int_net_name)
    if context.properties['numNics'] > 3:
        depends_on_array.append(app_net_name)
    target_instance_name = generate_name(prefix, 'bigip-vm-01-ti')
    public_ip_name = generate_name(prefix, 'public-ip-01')

    depends_on_array.append(target_instance_name)
    dag_configuration = [{
      'name': 'dag',
      'type': '../modules/dag/dag.py',
      'properties': {
            'firewalls' : firewalls_config,
            'computeAddresses': [
                {
                  'name': public_ip_name,
                  'region': context.properties['region'],
                }
            ],
            'forwardingRules': [
                {
                    'name': context.properties['uniqueString'] + '-fr-01',
                    'region': context.properties['region'],
                    'IPAddress': '$(ref.' + public_ip_name + '.selfLink)',
                    'IPProtocol': 'TCP',
                    'target': '$(ref.' + target_instance_name + '.selfLink)',
                    'loadBalancingScheme': 'EXTERNAL'
                }
            ],
            'healthChecks': [
                {
                    'checkIntervalSec': 5,
                    'description': 'my tcp healthcheck',
                    'name': context.properties['uniqueString'] + '-tcp-hc',
                    'tcpHealthCheck': {
                        'port': 44000
                    },
                    'timeoutSec': 5,
                    'type': 'TCP'
                },
                {
                    'checkIntervalSec': 5,
                    'description': 'my http healthcheck',
                    'name': context.properties['uniqueString'] + '-http-hc',
                    'httpHealthCheck': {
                        'port': 80
                    },
                    'timeoutSec': 5,
                    'type': 'HTTP'
                },
                {
                    'checkIntervalSec': 5,
                    'description': 'my https healthcheck',
                    'name': context.properties['uniqueString'] + '-https-hc',
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
    application_instance_name= generate_name(prefix, 'application-vm-01')
    bastion_instance_name= generate_name(prefix, 'bastion-vm-01')
    bigip_instance_name= generate_name(prefix, 'bigip-vm-01')
    fr_name = generate_name(prefix, 'fr-01')
    mgmt_net_name = generate_name(prefix, 'mgmt-network')
    ext_net_name = generate_name(prefix, 'ext-network')
    int_net_name = generate_name(prefix, 'int-network-0' + \
            str(context.properties['numNics'] - 1))

    resources = create_network_deployment(context) + create_bigip_deployment(context) \
    + create_application_deployment(context) + create_dag_deployment(context)
    outputs = []
    mgmt_nic_index = '0' if context.properties['numNics'] == 1 else '1'
    mgmt_port = '8443' if context.properties['numNics'] == 1 else '443'

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

    if context.properties['numNics'] == 2:
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

    if context.properties['numNics'] == 3:
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
            'value': '$(ref.' + fr_name + '.IPAddress)'
        },
        {
            'name': 'vip1PublicUrlHttp',
            'value': 'http://' + '$(ref.' + fr_name + '.IPAddress)'
        },
        {
            'name': 'vip1PublicUrlHttps',
            'value': 'https://' + '$(ref.' + fr_name + '.IPAddress)'
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
