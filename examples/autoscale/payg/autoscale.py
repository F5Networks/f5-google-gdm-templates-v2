# Copyright 2021 F5 Networks All rights reserved.
#
# Version 3.3.0.0

# pylint: disable=W,C,R

"""Creates the application."""
COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'


def generate_name(prefix, suffix):
    """Generate unique name."""
    return prefix + "-" + suffix

def create_network_deployment(context):
    """Create template deployment."""
    deployment = {
        'name': 'network',
        'type': '../../modules/network/network.py',
        'properties': {
            'name': 'network',
            'uniqueString': context.properties['uniqueString'],
            'provisionPublicIp': context.properties['provisionPublicIp'],
            'region': context.properties['region'],
            'subnets': [{
                'description': 'Subnetwork used for management',
                'name': 'mgmt-subnet',
                'region': context.properties['region'],
                'ipCidrRange': '10.0.0.0/24'
            },
            {
                'description': 'Subnetwork used for application services',
                'name': 'app-subnet',
                'region': context.properties['region'],
                'ipCidrRange': '10.0.1.0/24'
            }]
        }
    }
    return deployment

def create_access_deployment(context):
    """Create template deployment."""
    deployment = {
      'name': 'access',
      'type': '../../modules/access/access.py',
      'properties': {
        'solutionType': 'secret',
        'uniqueString': context.properties['uniqueString']
      }
    }
    return deployment

def create_application_deployment(context):
    """Create template deployment."""
    prefix = context.properties['uniqueString']
    net_name = generate_name(prefix, 'network')
    subnet_name = generate_name(prefix, 'app-subnet')
    zones = []
    for zone in context.properties['zones']:
        zones = zones + [{'zone': 'zones/' + zone}]
    depends_on_array = []
    if not context.properties['update']:
        depends_on_array.append(net_name)
        depends_on_array.append(subnet_name)
    deployment = {
      'name': 'application',
      'type': '../../modules/application/application.py',
      'properties': {
        'appContainerName': context.properties['appContainerName'],
        'application': context.properties['application'],
        'autoscalers': [{
            'name': 'f5-demo',
            'zone': context.properties['zones'][0]
        }],
        'cost': context.properties['cost'],
        'environment': context.properties['environment'],
        'group': context.properties['group'],
        'instanceGroupManagers': [{
            'name': 'f5-demo',
            'distributionPolicy': {
                'targetShape': 'EVEN',
                'zones': zones
            }
        }],
        'instanceTemplates': [{
            'name': 'f5-demo',
            'networkInterfaces': [{
                'accessConfigs': [{
                    'name': 'External NAT',
                    'type': 'ONE_TO_ONE_NAT'
                }],
                'description': 'Interface used for external traffic',
                'network': '$(ref.' + net_name + '.selfLink)',
                'subnetwork': '$(ref.' + subnet_name + '.selfLink)'
            }]
        }],
        'instanceTemplateVersion': 1,
        'instanceType': 'n1-standard-1',
        'owner': context.properties['owner'],
        'region': context.properties['region'],
        'uniqueString': context.properties['uniqueString']
      },
      'metadata': {
        'dependsOn': depends_on_array
      }
    }
    return deployment

def create_bastion_deployment(context):
    """Create template deployment."""
    prefix = context.properties['uniqueString']
    net_name = generate_name(prefix, 'network')
    subnet_name = generate_name(prefix, 'mgmt-subnet')
    zones = []
    for zone in context.properties['zones']:
        zones = zones + [{'zone': 'zones/' + zone}]
    depends_on_array = []
    if not context.properties['update']:
        depends_on_array.append(net_name)
        depends_on_array.append(subnet_name)
    deployment = {
      'name': 'bastion',
      'type': '../../modules/bastion/bastion.py',
      'properties': {
        'application': context.properties['application'],
        'autoscalers': [{
            'name': 'bastion',
            'zone': context.properties['zones'][0]
        }],
        'cost': context.properties['cost'],
        'environment': context.properties['environment'],
        'group': context.properties['group'],
        'instanceGroupManagers': [{
            'name': 'bastion',
            'distributionPolicy': {
                'targetShape': 'EVEN',
                'zones': zones
            }
        }],
        'instanceTemplates': [{
            'name': 'bastion',
            'networkInterfaces': [{
                'accessConfigs': [{
                    'name': 'External NAT',
                    'type': 'ONE_TO_ONE_NAT'
                }],
                'description': 'Interface used for external traffic',
                'network': '$(ref.' + net_name + '.selfLink)',
                'subnetwork': '$(ref.' + subnet_name + '.selfLink)'
            }]
        }],
        'owner': context.properties['owner'],
        'region': context.properties['region'],
        'uniqueString': context.properties['uniqueString']
      },
      'metadata': {
        'dependsOn': depends_on_array
      }
    }
    return deployment

def create_bigip_deployment(context):
    """ Create template deployment """
    prefix = context.properties['uniqueString']
    net_name = generate_name(prefix, 'network')
    subnet_name = generate_name(prefix, 'mgmt-subnet')
    allow_usage_analytics = context.properties['allowUsageAnalytics'] if \
        'allowUsageAnalytics' in context.properties else True
    custom_image_id = context.properties['bigIpCustomImageId'] if \
        'bigIpCustomImageId' in context.properties else ''
    secret_id = context.properties['bigIpSecretId'] if \
        'bigIpSecretId' in context.properties else ''
    service_account_email = context.properties['bigIpServiceAccountEmail'] if \
        'bigIpServiceAccountEmail' in context.properties else \
            context.properties['uniqueString'] + \
                '-admin@' + \
                    context.env['project'] + \
                        '.iam.gserviceaccount.com'
    zones = []
    for zone in context.properties['zones']:
        zones = zones + [{'zone': 'zones/' + zone}]
    depends_on_array = []
    if not context.properties['update']:
        depends_on_array.append(net_name)
        depends_on_array.append(subnet_name)
        net_ref = '$(ref.' + net_name + '.selfLink)'
        sub_ref = '$(ref.' + subnet_name + '.selfLink)'
    else:
        net_ref = COMPUTE_URL_BASE + 'projects/' + \
                  context.env['project'] + '/global/networks/' + net_name
        sub_ref = COMPUTE_URL_BASE + 'projects/' + context.env['project'] + \
                      '/regions/' + context.properties['region'] + \
                              '/subnetworks/' + subnet_name
    deployment = {
        'name': 'bigip-autoscale',
        'type': '../../modules/bigip-autoscale/bigip_autoscale.py',
        'properties': {
          'allowUsageAnalytics': allow_usage_analytics,
          'application': context.properties['application'],
          'bigIpRuntimeInitConfig': context.properties['bigIpRuntimeInitConfig'],
          'bigIpRuntimeInitPackageUrl': context.properties['bigIpRuntimeInitPackageUrl'],
          'autoscalers': [{
              'name': 'bigip',
              'zone': context.properties['zones'][0],
              'autoscalingPolicy': {
                'minNumReplicas': context.properties['bigIpScalingMinSize'],
                'maxNumReplicas': context.properties['bigIpScalingMaxSize'],
                'cpuUtilization': {
                  'utilizationTarget': context.properties['bigIpScaleOutCpuThreshold']
                },
                'coolDownPeriodSec': context.properties['bigIpCoolDownPeriodSec'],
                'customMetricUtilizations': [
                    {
                        'metric': 'custom.googleapis.com/system/cpu',
                        'filter': 'resource.type = \"generic_node\"',
                        'utilizationTarget': 60,
                        'utilizationTargetType': 'GAUGE'
                    }
                ]
              }
          }],
          'cost': context.properties['cost'],
          'customImageId': custom_image_id,
          'environment': context.properties['environment'],
          'group': context.properties['group'],
          'healthChecks': [
              {
                  'checkIntervalSec': 5,
                  'description': 'BIG-IP external VIP healthcheck',
                  'httpHealthCheck': {
                      'port': 80
                  },
                  'timeoutSec': 5,
                  'type': 'HTTP'
              }
          ],
          'imageName': context.properties['bigIpImageName'],
          'instanceGroupManagers': [{
            'name': 'bigip',
            'distributionPolicy': {
                'targetShape': 'EVEN',
                'zones': zones
            }
          }],
          'instanceTemplates': [{
              'name': 'bigip'
          }],
          'instanceTemplateVersion': context.properties['bigIpInstanceTemplateVersion'],
          'instanceType': context.properties['bigIpInstanceType'],
          'logId': context.properties['logId'],
          'networkSelfLink': net_ref,
          'owner': context.properties['owner'],
          'project': context.env['project'],
          'provisionPublicIp': context.properties['provisionPublicIp'],
          'region': context.properties['region'],
          'secretId': secret_id,
          'serviceAccountEmail': service_account_email,
          'subnetSelfLink': sub_ref,
          'targetPools': [{
              'name': 'bigip',
              'region': context.properties['region']
          }],
          'uniqueString': context.properties['uniqueString']
        },
        'metadata': {
            'dependsOn': depends_on_array
        }
    }
    return deployment

def create_dag_deployment(context):
    """ Create template deployment """
    prefix = context.properties['uniqueString']
    net_name = generate_name(prefix, 'network')
    subnet_name = generate_name(prefix, 'mgmt-subnet')
    target_pool_name = generate_name(prefix, 'bigip-tp')
    instance_group_name = generate_name(prefix, 'bigip-igm')
    firewalls_config = [
        {
            'allowed': [
                {
                    'IPProtocol': 'TCP',
                    'ports': [ 22, 8443, 443 ]
                }
            ],
            'description': 'Allow ssh and 443/8443 to management',
            'name': context.properties['uniqueString'] + '-mgmt-fw',
            'network': '$(ref.' + net_name + '.selfLink)',
            'sourceRanges': [ context.properties['restrictedSrcAddressMgmt'] if context.properties['provisionPublicIp'] else '10.0.0.0/24' ],
            'targetTags': [ context.properties['uniqueString'] + '-mgmt-fw' ]
        },
        {
            'allowed': [
                {
                    'IPProtocol': 'TCP',
                    'ports': [ 80, 443 ]
                }
            ],
            'description': 'Allow web traffic to public network',
            'name': context.properties['uniqueString'] + '-app-int-fw',
            'network': '$(ref.' + net_name + '.selfLink)',
            'sourceRanges': [ '10.0.0.0/24' ],
            'targetTags': [ context.properties['uniqueString'] + '-app-int-fw' ]
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
            'network': '$(ref.' + net_name + '.selfLink)',
            'sourceRanges': [ context.properties['restrictedSrcAddressApp'] ],
            'targetTags': [ context.properties['uniqueString'] + '-app-vip-fw' ]
        }
    ]
    bastion_firewall_config = {
        'allowed': [
            {
                'IPProtocol': 'TCP',
                'ports': [ 22, 8443, 443 ]
            }
        ],
        'description': 'Allow ssh and 443/8443 to bastion',
        'name': context.properties['uniqueString'] + '-bastion-fw',
        'network': '$(ref.' + net_name + '.selfLink)',
        'sourceRanges': [ 
            context.properties['restrictedSrcAddressMgmt']
        ],
        'targetTags': [ generate_name(prefix, 'bastion-fw') ]
    }
    if not context.properties['provisionPublicIp']:
        firewalls_config.append(bastion_firewall_config)
    depends_on_array = []
    if not context.properties['update']:
        depends_on_array.append(net_name)
        depends_on_array.append(subnet_name)
        depends_on_array.append(target_pool_name)
        depends_on_array.append(instance_group_name)
    deployment = {
      'name': 'dag',
      'type': '../../modules/dag/dag.py',
      'properties': {
        'firewalls' : firewalls_config,
        'forwardingRules': [
            {
                'name': context.properties['uniqueString'] + '-fr-01',
                'region': context.properties['region'],
                'IPProtocol': 'TCP',
                'target': '$(ref.' + target_pool_name + '.selfLink)',
                'loadBalancingScheme': 'EXTERNAL'
            }
        ],
        'backendServices': [
            {
                'backends': [
                    {
                        'group': '$(ref.' + instance_group_name + '.instanceGroup)'
                    }
                ],
                'description': 'Backend service used for internal LB',
                'healthChecks': [
                    '$(ref.' + context.properties['uniqueString'] + '-tcp-hc.selfLink)'
                ],
                'loadBalancingScheme': 'INTERNAL',
                'name': context.properties['uniqueString'] + '-bes',
                'network': '$(ref.' + net_name + '.selfLink)',
                'protocol': 'TCP',
                'region': context.properties['region'],
                'sessionAffinity': 'CLIENT_IP'
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
    }
    return deployment

def generate_config(context):
    """ Entry point for the deployment resources. """

    name = context.properties.get('name') or \
           context.env['name']
    prefix = context.properties['uniqueString']

    deployment_name = generate_name(prefix, name)
    application_igm_name= generate_name(prefix, 'f5-demo-igm')
    bastion_igm_name= generate_name(prefix, 'bastion-igm')
    bigip_igm_name= generate_name(prefix, 'bigip-igm')
    fr_name = generate_name(prefix, 'fr-01')
    net_name = generate_name(prefix, 'network')

    resources = [create_network_deployment(context)] + \
                [create_application_deployment(context)] + \
                [create_bigip_deployment(context)] + \
                [create_dag_deployment(context)]
    outputs = []

    if not 'bigIpServiceAccountEmail' in context.properties:
        resources = resources + [create_access_deployment(context)]

    if not context.properties['provisionPublicIp']:
        resources = resources + [create_bastion_deployment(context)]
        outputs = outputs + [
            {
                'name': 'bastionInstanceGroupName',
                'value': bastion_igm_name
            },
            {
                'name': 'bastionInstanceGroupSelfLink',
                'value': '$(ref.' + bastion_igm_name + '.selfLink)'
            }
        ]

    outputs = outputs + [
        {
            'name': 'deploymentName',
            'value': deployment_name
        },
        {
            'name': 'appInstanceGroupName',
            'value': application_igm_name
        },
        {
            'name': 'appInstanceGroupSelfLink',
            'value': '$(ref.' + application_igm_name + '.selfLink)'
        },
        {
            'name': 'bigIpInstanceGroupName',
            'value': bigip_igm_name
        },
        {
            'name': 'bigIpInstanceGroupSelfLink',
            'value': '$(ref.' + bigip_igm_name + '.selfLink)'
        },
        {
            'name': 'networkName',
            'value': net_name
        },
        {
            'name': 'networkSelfLink',
            'value': '$(ref.' + net_name + '.selfLink)'
        },
        {
            'name': 'wafExternalHttpUrl',
            'value': 'http://' + '$(ref.' + fr_name + '.IPAddress)'
        },
        {
            'name': 'wafExternalHttpsUrl',
            'value': 'https://' + '$(ref.' + fr_name + '.IPAddress)'
        },
        {
            'name': 'wafPublicIp',
            'value': '$(ref.' + fr_name + '.IPAddress)'
        }
    ]

    return {
        'resources':
            resources,
        'outputs':
            outputs
    }
