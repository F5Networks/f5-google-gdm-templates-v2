# Copyright 2021 F5 Networks All rights reserved.
#
# Version 2.2.0.0

# pylint: disable=W,C,R

"""Creates the application."""
COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'


def generate_name(prefix, suffix):
    """Generate unique name."""
    return prefix + "-" + suffix

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

def create_bigip_deployment(context):
    """ Create template deployment """
    prefix = context.properties['uniqueString']
    net_name = context.properties['networkName']
    subnet_name = context.properties['subnets']['mgmtSubnetName']
    net_ref = COMPUTE_URL_BASE + 'projects/' + \
              context.env['project'] + '/global/networks/' + net_name
    sub_ref = COMPUTE_URL_BASE + 'projects/' + context.env['project'] + \
          '/regions/' + context.properties['region'] + \
          '/subnetworks/' + subnet_name
    depends_on_array = []
    deployment = {
        'name': 'bigip',
        'type': '../../modules/bigip-autoscale/bigip_autoscale.py',
        'properties': {
          'application': context.properties['application'],
          'availabilityZone': context.properties['zone'],
          'bigIpRuntimeInitConfig': context.properties['bigIpRuntimeInitConfig'],
          'bigIpRuntimeInitPackageUrl': context.properties['bigIpRuntimeInitPackageUrl'],
          'autoscalers': [{
              'name': 'bigip',
              'zone': context.properties['zone'],
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
              'zone': context.properties['zone']
          }],
          'instanceTemplates': [{
              'name': 'bigip'
          }],
          'instanceTemplateVersion': context.properties['bigIpInstanceTemplateVersion'],
          'instanceType': context.properties['bigIpInstanceType'],
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
    net_name = context.properties['networkName']
    subnet_name = context.properties['subnets']['mgmtSubnetName']
    net_ref = COMPUTE_URL_BASE + 'projects/' + \
              context.env['project'] + '/global/networks/' + net_name
    sub_ref = COMPUTE_URL_BASE + 'projects/' + context.env['project'] + \
          '/regions/' + context.properties['region'] + \
          '/subnetworks/' + subnet_name
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
                'network': net_ref,
                'sourceRanges': [ context.properties['restrictedSrcAddressMgmt'] ],
                'targetTags': [ context.properties['uniqueString'] + '-mgmt-fw' ]
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
                'network': net_ref,
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
    prefix = context.properties['uniqueString']

    deployment_name = generate_name(prefix, name)
    bigip_igm_name= generate_name(prefix, 'bigip-igm')
    fw_rule_name = generate_name(prefix, 'fwrule1')

    resources = [create_access_deployment(context)] + \
                [create_bigip_deployment(context)] + \
                [create_dag_deployment(context)]
    outputs = []

    outputs = outputs + [
        {
            'name': 'deploymentName',
            'value': deployment_name
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
            'name': 'wafExternalHttpUrl',
            'value': 'http://' + '$(ref.' + fw_rule_name + '.IPAddress)'
        },
        {
            'name': 'wafExternalHttpsUrl',
            'value': 'https://' + '$(ref.' + fw_rule_name + '.IPAddress)'
        },
        {
            'name': 'wafPublicIp',
            'value': '$(ref.' + fw_rule_name + '.IPAddress)'
        }
    ]

    return {
        'resources':
            resources,
        'outputs':
            outputs
    }
