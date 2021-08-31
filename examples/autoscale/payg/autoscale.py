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
        'availabilityZone': context.properties['availabilityZone'],
        'cost': context.properties['cost'],
        'createAutoscaleGroup': True,
        'environment': context.properties['environment'],
        'group': context.properties['group'],
        'instanceTemplateVersion': 1,
        'instanceType': 'n1-standard-1',
        'networkSelfLink': '$(ref.' + net_name + '.selfLink)',
        'subnetSelfLink': '$(ref.' + subnet_name + '.selfLink)',
        'uniqueString': context.properties['uniqueString'],
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
            'availabilityZone': context.properties['availabilityZone'],
            'cost': context.properties['cost'],
            'createAutoscaleGroup': True,
            'environment': context.properties['environment'],
            'group': context.properties['group'],
            'osImage': 'projects/ubuntu-os-cloud/global/images/family/ubuntu-1604-lts',
            'instanceTemplateVersion': 1,
            'instanceType': 'n1-standard-1',
            'networkSelfLink': '$(ref.' + net_name + '.selfLink)',
            'subnetSelfLink': '$(ref.' + subnet_name + '.selfLink)',
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
          'availabilityZone': context.properties['availabilityZone'],
          'bigIpRuntimeInitConfig': context.properties['bigIpRuntimeInitConfig'],
          'bigIpRuntimeInitPackageUrl': context.properties['bigIpRuntimeInitPackageUrl'],
          'coolDownPeriodSec': context.properties['coolDownPeriodSec'],
          'cost': context.properties['cost'],
          'environment': context.properties['environment'],
          'group': context.properties['group'],
          'imageName': context.properties['imageName'],
          'instanceTemplateVersion': context.properties['instanceTemplateVersion'],
          'instanceType': context.properties['instanceType'],
          'maxNumReplicas': context.properties['maxNumReplicas'],
          'minNumReplicas': context.properties['minNumReplicas'],
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
          'uniqueString': context.properties['uniqueString'],
          'utilizationTarget': context.properties['utilizationTarget']
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
        'application': context.properties['application'],
        'applicationPort': '80 443',
        'applicationVipPort': '80 443',
        'cost': context.properties['cost'],
        'environment': context.properties['environment'],
        'group': context.properties['group'],
        'guiPortMgmt': 8443,
        'instanceGroups': '$(ref.' + instance_group_name + '.selfLink)',
        'networkSelfLinkApp': '$(ref.' + net_name + '.selfLink)',
        'networkSelfLinkMgmt': '$(ref.' + net_name + '.selfLink)',
        'numberOfForwardingRules': 1,
        'numberOfInternalForwardingRules': 0,
        'numberOfNics': 1,
        'owner': context.properties['owner'],
        'region': context.properties['region'],
        'restrictedSrcAddressApp': context.properties['restrictedSrcAddressApp'],
        'restrictedSrcAddressAppInternal': context.properties['restrictedSrcAddressAppInternal'],
        'restrictedSrcAddressMgmt': context.properties['restrictedSrcAddressMgmt'],
        'targetPoolSelfLink': '$(ref.' + target_pool_name + '.selfLink)',
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
