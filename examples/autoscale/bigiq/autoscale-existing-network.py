# Copyright 2021 F5 Networks All rights reserved.
#
# Version 3.1.0.0

# pylint: disable=W,C,R

"""Creates the application."""
import re
COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'


def generate_name(prefix, suffix):
    """Generate unique name."""

    return prefix + '-' + suffix

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
    if context.shared_vpc == 'true':
        net_ref = net_name
        sub_ref = subnet_name
    else:
        net_ref = COMPUTE_URL_BASE + 'projects/' + \
                context.env['project'] + '/global/networks/' + net_name
        sub_ref = COMPUTE_URL_BASE + 'projects/' + context.env['project'] + \
                '/regions/' + context.properties['region'] + \
                '/subnetworks/' + subnet_name
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
    deployment = {
        'name': 'bigip-autoscale',
        'type': '../../modules/bigip-autoscale/bigip_autoscale.py',
        'properties': {
          'allowUsageAnalytics': allow_usage_analytics,
          'application': context.properties['application'],
          'bigIpRuntimeInitConfig': context.properties['bigIpRuntimeInitConfig'],
          'bigIpRuntimeInitPackageUrl': context.properties['bigIpRuntimeInitPackageUrl'],
          'bigIqSecretId': context.properties['bigIqSecretId'],
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
    net_name = context.properties['networkName']
    subnet_name = context.properties['subnets']['mgmtSubnetName']
    if context.shared_vpc == 'true':
        net_ref = net_name
        sub_ref = subnet_name
    else:
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

def create_function_deployment(context):
    """ Create template deployment """

    prefix = context.properties['uniqueString']
    function_name = generate_name(prefix, 'function')
    instance_group_name = generate_name(prefix, 'bigip-igm')
    topic_name = generate_name(prefix, 'topic')
    job_name = generate_name(prefix, 'job')
    topic_path = 'projects/' + context.env['project'] + \
                        '/topics/' + \
                            topic_name
    depends_on_array = []
    if not context.properties['update']:
        depends_on_array.append(function_name)
        depends_on_array.append(instance_group_name)
        depends_on_array.append(topic_name)
        depends_on_array.append(topic_path)
        depends_on_array.append(job_name)
    deployment = {
      'name': 'function',
      'type': '../../modules/function/function.py',
      'properties': {
        'jobs': [
          {
            'name': job_name,
            'schedule': '* * * * *',
            'timeZone': 'America/Los_Angeles',
            'pubsubTarget': {
              'topicName': topic_path,
              'data': 'VGhpcyBteSBoZWxsbyBtZXNzYWdl'
            }
          }
        ],
        'topics': [
          {
            'name': topic_path,
            'topic': topic_name,
            'labels': {
                'delete': 'true'
            }
          }
        ],
        'functions': [
          {
            'name': function_name,
            'serviceAccountEmail': context.env['project'] + '@appspot.gserviceaccount.com',
            'sourceArchiveUrl': 'gs://f5-gcp-bigiq-revoke-us/develop/v1.0.0/cloud_functions_bigiq_revoke.zip',
            'entryPoint': 'revoke_bigiq_pubsub',
            'eventTrigger': {
              'eventType': 'google.pubsub.topic.publish',
              'resource': topic_path
            },
            'runtime': 'python37',
            'maxInstances': 10,
            'environmentVariables': {
              'bigIpRuntimeInitConfig': context.properties['bigIpRuntimeInitConfig'],
              'bigipInstanceGroup': instance_group_name,
              'zone': context.properties['zones'][0]
            },
            'labels': {
                'delete': 'true'
            }
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
    bigip_igm_name = generate_name(prefix, 'bigip-igm')
    fr_name = generate_name(prefix, 'fr-01')

    net_match = re.search(r'^projects/[a-z]([-a-z0-9]*[a-z0-9])?/global/networks/[a-z]([-a-z0-9]*[a-z0-9])?', \
                context.properties['networkName'])
    subnet_match = re.search(r'^projects/[a-z]([-a-z0-9]*[a-z0-9])?/regions/[a-z]([-a-z0-9]*[a-z0-9])/subnetworks/[a-z]([-a-z0-9]*[a-z0-9])?', \
                context.properties['subnets']['mgmtSubnetName'])
    context.shared_vpc = 'true' if net_match and subnet_match else 'false'

    resources = [create_bigip_deployment(context)] + \
                [create_dag_deployment(context)] + \
                [create_function_deployment(context)]
    outputs = []

    if not 'bigIpServiceAccountEmail' in context.properties:
        resources = resources + [create_access_deployment(context)]

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
