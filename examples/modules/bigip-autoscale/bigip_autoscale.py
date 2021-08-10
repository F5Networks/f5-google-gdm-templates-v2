# Copyright 2021 F5 Networks All rights reserved.
#
# Version 0.1.0

# pylint: disable=W,C,R

"""Creates the application"""
COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'


def generate_name(prefix, suffix):
    """ Generate unique name """
    return prefix + "-" + suffix

def create_instance_template(context, instance_template_name):
    """ Create autoscale instance template """
    instance_template = {
        'name': instance_template_name,
        'type': 'bigip_instance_template.py',
        'properties': {
            'application': context.properties['application'],
            'bigIpRuntimeInitConfig': context.properties['bigIpRuntimeInitConfig'],
            'bigIpRuntimeInitPackageUrl': context.properties['bigIpRuntimeInitPackageUrl'],
            'cost': context.properties['cost'],
            'environment': context.properties['environment'],
            'group': context.properties['group'],
            'imageName': context.properties['imageName'],
            'instanceType': context.properties['instanceType'],
            'networkSelfLink': context.properties['networkSelfLink'], # depends on network
            'provisionPublicIp': context.properties['provisionPublicIp'],
            'owner': context.properties['owner'],
            'region': context.properties['region'],
            'serviceAccountEmail': context.properties['serviceAccountEmail'], # depends on access
            'subnetSelfLink': context.properties['subnetSelfLink'], # depends on network
            'uniqueString': context.properties['uniqueString']
        }
    }
    return instance_template

def create_instance_group(context, instance_template_name):
    """ Create autoscale instance group """
    instance_group = {
        'name': context.env['deployment'] + '-igm',
        'type': 'compute.v1.instanceGroupManager',
        'properties': {
            'baseInstanceName': context.env['deployment'] + '-vm',
            'instanceTemplate': '$(ref.' + instance_template_name + '.selfLink)', # depends on instance template
            'targetPools': ['$(ref.' + context.env['deployment'] + '-tp.selfLink)'], # depends on target pool
            'targetSize': 2,
            'updatePolicy': {
                'minimalAction': 'REPLACE',
                'type': 'PROACTIVE'
            },
            'zone': context.properties['availabilityZone']
        }
    }
    return instance_group

def create_autoscaler(context):
    """ Create autoscaler """
    autoscaler = {
        'name': context.env['deployment'] + '-as',
        'type': 'compute.v1.autoscalers',
        'properties': {
            'zone': context.properties['availabilityZone'],
            'target': '$(ref.' + context.env['deployment'] + '-igm.selfLink)', # depends on instance group manager
            'autoscalingPolicy': {
                "minNumReplicas": context.properties['minNumReplicas'],
                'maxNumReplicas': context.properties['maxNumReplicas'],
                'cpuUtilization': {
                    'utilizationTarget': context.properties['utilizationTarget']
                },
                'coolDownPeriodSec': context.properties['coolDownPeriodSec']
            }
        }
    }
    return autoscaler

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
            'healthChecks': ['$(ref.' + context.env['deployment'] + '-external.selfLink)'], # depends on health check
        }
    }
    return target_pool

def create_target_pool_outputs(context):
    """ Create target pool outputs """
    target_pool = {
        'name': 'targetPool',
        'resourceName': context.env['deployment'] + '-tp',
        'value': '$(ref.' + context.env['deployment'] + '-tp.selfLink)' # depends on target pool
    }
    return target_pool

def create_instance_group_output(context):
    """ Create instance group output """
    instance_group = {
        'name': 'instanceGroupName',
        'value': ''.join([COMPUTE_URL_BASE,
                          'projects/',
                          context.properties['project'],
                          '/zones/',
                          context.properties['availabilityZone'],
                          '/instanceGroups/',
                          context.env['deployment'],
                          '-igm'
                          ])
    }
    return instance_group

def generate_config(context):
    """ Entry point for the deployment resources. """

    name = context.properties.get('name') or \
           context.env['name']
    bigip_autoscale_deployment_name = generate_name(context.properties['uniqueString'], name)
    instance_template_name = context.env['deployment'] + \
        '-template-v' + \
            str(context.properties['instanceTemplateVersion'])

    resources = []
    resources = resources + [create_instance_template(context, instance_template_name)] + \
                [create_target_pool(context)] + \
                [create_health_check(context, 'external')] + \
                [create_instance_group(context, instance_template_name)] + \
                [create_autoscaler(context)]

    outputs = [
        {
            'name': 'bigipAutoscaleName',
            'value': bigip_autoscale_deployment_name
        }
    ]

    outputs = outputs + [create_instance_group_output(context), create_target_pool_outputs(context)]

    return {
        'resources':
            resources,
        'outputs':
            outputs
    }
