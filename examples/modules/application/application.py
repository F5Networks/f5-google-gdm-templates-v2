# Copyright 2021 F5 Networks All rights reserved.
#
# Version 0.1.0

"""Creates the application"""
COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'


def generate_name(prefix, suffix):
    """ Generate unique name """
    return prefix + "-" + suffix

def create_instance(context, application_name):
    """ Create standalone instance """
    instance = {
        'name': application_name,
        'type': 'compute.v1.instance',
        'properties': {
            'zone': context.properties['availabilityZone'],
            'hostname': context.properties['hostname'],
            'tags': {
                'items': ['appfwint-'+ context.properties['uniqueString']]
            },
            'machineType': ''.join([COMPUTE_URL_BASE, 'projects/',
                                    context.env['project'], '/zones/',
                                    context.properties['availabilityZone'],
                                    '/machineTypes/',
                                    context.properties['instanceType']]),
            'disks': [{
                'deviceName': 'boot',
                'type': 'PERSISTENT',
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': ''.join([COMPUTE_URL_BASE, 'projects/',
                                            'centos-cloud/global/',
                                            'images/centos-7-v20210701'])
                }
            }],
            'networkInterfaces': [{
                'network': context.properties['networkSelfLink'],
                'subnetwork': context.properties['subnetSelfLink'],
                'accessConfigs': [{
                    'name': 'External NAT',
                    'type': 'ONE_TO_ONE_NAT'
                }]
            }],
            'metadata': {
                'items': [{
                    'key': 'startup-script',
                    'value': ''.join(['#!/bin/bash\n',
                                        'yum -y install docker\n',
                                        'service docker start\n',
                                        'docker run --name f5demo -p 80:80 -p 443:443 -d ',
                                        context.properties['appContainerName']])
                }]
            }
        }
    }
    return instance

def create_instance_template(context, application_name):
    """ Create autoscale instance template """
    instance_template = {
        'name': application_name + '-template',
        'type': 'compute.v1.instanceTemplate',
        'properties': {
            'properties': {
                'tags': {
                    'items': ['appfwint-'+ context.properties['uniqueString']]
                },
                'machineType': context.properties['instanceType'],
                'disks': [{
                    'deviceName': 'boot',
                    'type': 'PERSISTENT',
                    'boot': True,
                    'autoDelete': True,
                    'initializeParams': {
                        'sourceImage': ''.join([COMPUTE_URL_BASE, 'projects/',
                                            'centos-cloud/global/',
                                            'images/centos-7-v20210701'])
                    }
                }],
                'networkInterfaces': [{
                    'network': context.properties['networkSelfLink'],
                    'subnetwork': context.properties['subnetSelfLink'],
                    'accessConfigs': [{
                        'name': 'External NAT',
                        'type': 'ONE_TO_ONE_NAT'
                    }],
                }],
                'metadata': {
                    'items': [{
                        'key': 'startup-script',
                        'value': ''.join(['#!/bin/bash\n',
                                            'yum -y install docker\n',
                                            'service docker start\n',
                                            'docker run --name f5demo -p 80:80 -p 443:443 -d ',
                                            context.properties['appContainerName']])
                    }]
                }
            }
        }
    }
    return instance_template

def create_instance_group(context, application_name):
    """ Create autoscale instance group """
    instance_group = {
        'name': application_name + '-igm',
        'type': 'compute.v1.instanceGroupManager',
        'properties': {
            'baseInstanceName': application_name + 'vm',
            'instanceTemplate': '$(ref.' + application_name + '-template.selfLink)',
            'targetSize': 2,
            'zone': context.properties['availabilityZone']
        }
    }
    return instance_group

def create_autoscaler(context, application_name):
    """ Create autoscaler """
    autoscaler = {
        'name': application_name + '-as',
        'type': 'compute.v1.autoscalers',
        'properties': {
            'zone': context.properties['availabilityZone'],
            'target': '$(ref.' + application_name + '-igm.selfLink)',
            'autoscalingPolicy': {
                "minNumReplicas": 1,
                'maxNumReplicas': 8,
                'cpuUtilization': {
                    'utilizationTarget': 0.8
                },
                'coolDownPeriodSec': 60
            }
        }
    }
    return autoscaler

def create_application_ip_output(application_name):
    """ Create instance app IP output """
    application_ip = {
        'name': 'applicationIp',
        'value': '$(ref.{}.networkInterfaces[0].'
                    'accessConfigs[0].natIP)'.format(application_name)
    }
    return application_ip

def create_instance_group_output(application_name):
    """ Create instance group output """
    instance_group = {
        'name': 'instanceGroup',
        'value': '$(ref.' + application_name + '-igm.selfLink)'
    }
    return instance_group

def generate_config(context):
    """ Entry point for the deployment resources. """

    name = context.properties.get('name') or \
        context.env['name']
    application_name = generate_name(context.properties['uniqueString'], name)

    resources = []

    do_autoscale = context.properties['createAutoscaleGroup']
    if do_autoscale:
        resources = resources + [create_instance_template(context, application_name)] + \
            [create_instance_group(context, application_name)] + \
                [create_autoscaler(context, application_name)]
    else:
        resources = resources + [create_instance(context, application_name)]

    outputs = [
        {
            'name': 'applicationName',
            'value': application_name
        }
    ]

    if do_autoscale:
        outputs = outputs + [create_instance_group_output(application_name)]
    else:
        outputs = outputs + [create_application_ip_output(application_name)]

    return {
        'resources':
            resources,
        'outputs':
            outputs
    }
