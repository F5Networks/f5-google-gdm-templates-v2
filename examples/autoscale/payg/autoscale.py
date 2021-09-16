# Copyright 2021 F5 Networks All rights reserved.
#
# Version 0.1.0

# pylint: disable=W,C,R

"""Creates the application."""
COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'


def generate_name(prefix, suffix):
    """Generate unique name."""
    return prefix + "-" + suffix


def create_network_deployment(context):
    """Create template deployment."""
    deployment = {
        'name': 'f5',
        'type': '../../modules/network/network.py',
        'properties': {
            'name': 'f5',
            'uniqueString': context.properties['uniqueString'],
            'provisionPublicIp': context.properties['provisionPublicIp'],
            'region': context.properties['region'],
            'subnets': [{
                'description': 'Subnetwork used for management',
                'name': 'mgmt',
                'region': context.properties['region'],
                'ipCidrRange': '10.0.0.0/24'
            },
            {
                'description': 'Subnetwork used for application services',
                'name': 'app',
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
    net_name = generate_name(prefix, 'f5-network')
    subnet_name = generate_name(prefix, 'app-subnet')
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
            'zone': context.properties['zone']
        }],
        'cost': context.properties['cost'],
        'environment': context.properties['environment'],
        'group': context.properties['group'],
        'instanceGroupManagers': [{
          'name': 'f5-demo',
          'zone': context.properties['zone']
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
    net_name = generate_name(prefix, 'f5-network')
    subnet_name = generate_name(prefix, 'mgmt-subnet')
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
            'zone': context.properties['zone']
        }],
        'cost': context.properties['cost'],
        'environment': context.properties['environment'],
        'group': context.properties['group'],
        'instanceGroupManagers': [{
          'name': 'bastion',
          'zone': context.properties['zone']
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
    net_name = generate_name(prefix, 'f5-network')
    subnet_name = generate_name(prefix, 'mgmt-subnet')
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
        'name': 'bigip',
        'type': '../../modules/bigip-autoscale/bigip_autoscale.py',
        'properties': {
          'application': context.properties['application'],
          'availabilityZone': context.properties['zone'],
          'bigIpRuntimeInitConfig': context.properties['bigIpRuntimeInitConfig'],
          'bigIpRuntimeInitPackageUrl': context.properties['bigIpRuntimeInitPackageUrl'],
          'autoscalers': context.properties['autoscalers'],
          'cost': context.properties['cost'],
          'environment': context.properties['environment'],
          'group': context.properties['group'],
          'healthChecks': context.properties['healthChecks'],
          'imageName': context.properties['imageName'],
          'instanceGroupManagers': context.properties['instanceGroupManagers'],
          'instanceTemplates': context.properties['instanceTemplates'],
          'instanceTemplateVersion': context.properties['instanceTemplateVersion'],
          'instanceType': context.properties['instanceType'],
          'networkSelfLink': net_ref,
          'owner': context.properties['owner'],
          'project': context.env['project'],
          'provisionPublicIp': context.properties['provisionPublicIp'],
          'region': context.properties['region'],
          'serviceAccountEmail': context.properties['uniqueString'] + \
              '-admin@' + \
                  context.env['project'] + \
                      '.iam.gserviceaccount.com',
          'subnetSelfLink': sub_ref,
          'targetPools': context.properties['targetPools'],
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
    net_name = generate_name(prefix, 'f5-network')
    subnet_name = generate_name(prefix, 'mgmt-subnet')
    target_pool_name = generate_name(prefix, 'bigip-tp')
    instance_group_name = generate_name(prefix, 'bigip-igm')
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
        'firewalls' : [
            {
                'allowed': [
                    {
                        'IPProtocol': 'TCP',
                        'ports': [ 22, 8443, 443 ]
                    }
                ],
                'description': 'Allow ssh and 443 to management',
                'name': context.properties['uniqueString'] + '-mgmt-fw',
                'network': '$(ref.' + net_name + '.selfLink)',
                'sourceRanges': [ context.properties['restrictedSrcAddressMgmt'] ],
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
                'sourceRanges': [ context.properties['restrictedSrcAddressAppInternal'] ],
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
        ],
        'forwardingRules': [
            {
                'name': context.properties['uniqueString'] + '-fwrule1',
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
                    '$(ref.' + context.properties['uniqueString'] + '-tcp-healthcheck.selfLink)'
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
    }
    return deployment

def generate_config(context):
    """ Entry point for the deployment resources. """

    name = context.properties.get('name') or \
           context.env['name']
    deployment_name = generate_name(context.properties['uniqueString'], name)

    resources = [create_network_deployment(context)] + \
                [create_access_deployment(context)] + \
                [create_application_deployment(context)] + \
                [create_bigip_deployment(context)] + \
                [create_dag_deployment(context)]


    if not context.properties['provisionPublicIp']:
        resources = resources + [create_bastion_deployment(context)]

    outputs = [
        {
            'name': 'deploymentName',
            'value': deployment_name
        }
    ]

    return {
        'resources':
            resources,
        'outputs':
            outputs
    }
