# Copyright 2021 F5 Networks All rights reserved.
#
# Version 0.1.0

# pylint: disable=W,C,R

"""Creates the bastion"""
COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'


def generate_name(prefix, suffix):
    """ Generate unique name """
    return prefix + "-" + suffix

def create_instance(context, bastion_name):
    """ Create standalone instance """
    instance = {
        'name': bastion_name,
        'type': 'compute.v1.instance',
        'properties': {
            'zone': context.properties['availabilityZone'],
            'hostname': context.properties['hostname'],
            'labels': {
                'appautoscalegroup': context.properties['uniqueString']
            },
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
                    'sourceImage': 'projects/ubuntu-os-cloud/global/images/family/ubuntu-1604-lts'
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
                    'value': ''.join([
                        '#!/bin/bash\n',
                        'sudo sh -c \'echo "***** Welcome to Bastion Host *****" > /etc/motd\'\n',
                        'echo "[INFO] Configure SSH Port"\n',
                        'sudo sh -c \'awk \'!/Port/\' /etc/ssh/sshd_config > temp && mv temp /etc/ssh/sshd_config\'\n',
                        'sudo sh -c \'echo "Port 22" >> /etc/ssh/sshd_config\'\n',
                        'echo "[INFO] Configuring X11 forwarding"\n',
                        'sudo sh -c \'awk \'!/X11Forwarding/\' /etc/ssh/sshd_config > temp && mv temp /etc/ssh/sshd_config\'\n',
                        'sudo sh -c \'echo "X11Forwarding yes" >> /etc/ssh/sshd_config\'\n',
                        'echo "[INFO] Done."\n',
                    ])
                }]
            }
        }
    }
    return instance

def create_instance_template(context, instance_template_name):
    """ Create autoscale instance template """
    instance_template = {
        'name': instance_template_name,
        'type': 'bastion_instance_template.py',
        'properties': {
            'application': context.properties['application'],
            'cost': context.properties['cost'],
            'environment': context.properties['environment'],
            'group': context.properties['group'],
            'instanceType': context.properties['instanceType'],
            'networkSelfLink': context.properties['networkSelfLink'],
            'owner': context.properties['owner'],
            'subnetSelfLink': context.properties['subnetSelfLink'],
            'uniqueString': context.properties['uniqueString']
        }
    }
    return instance_template

def create_instance_group(context, bastion_name, instance_template_name):
    """ Create autoscale instance group """
    instance_group = {
        'name': bastion_name + '-igm',
        'type': 'compute.v1.instanceGroupManager',
        'properties': {
            'baseInstanceName': bastion_name + 'vm',
            'instanceTemplate': '$(ref.' + instance_template_name + '.selfLink)',
            'targetSize': 2,
            'updatePolicy': {
                'minimalAction': 'REPLACE',
                'type': 'PROACTIVE'
            },
            'zone': context.properties['availabilityZone']
        }
    }
    return instance_group

def create_autoscaler(context, bastion_name):
    """ Create autoscaler """
    autoscaler = {
        'name': bastion_name + '-as',
        'type': 'compute.v1.autoscalers',
        'properties': {
            'zone': context.properties['availabilityZone'],
            'target': '$(ref.' + bastion_name + '-igm.selfLink)',
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

def create_bastion_ip_output(bastion_name):
    """ Create instance app IP output """
    bastion_ip = {
        'name': 'bastionIp',
        'value': '$(ref.{}.networkInterfaces[0].'
                    'accessConfigs[0].natIP)'.format(bastion_name)
    }
    return bastion_ip

def create_instance_group_output(bastion_name):
    """ Create instance group output """
    instance_group = {
        'name': 'instanceGroup',
        'value': '$(ref.' + bastion_name + '-igm.selfLink)'
    }
    return instance_group

def generate_config(context):
    """ Entry point for the deployment resources. """

    name = context.properties.get('name') or \
        context.env['name']
    bastion_name = generate_name(context.properties['uniqueString'], name)
    instance_template_name = bastion_name + '-template-v' + \
            str(context.properties['instanceTemplateVersion'])

    resources = []
    do_autoscale = context.properties['createAutoscaleGroup']
    if do_autoscale:
        resources = resources + [create_instance_template(context, instance_template_name)] + \
            [create_instance_group(context, bastion_name, instance_template_name)] + \
                [create_autoscaler(context, bastion_name)]
    else:
        resources = resources + [create_instance(context, bastion_name)]

    outputs = [
        {
            'name': 'bastionName',
            'value': bastion_name
        }
    ]

    if do_autoscale:
        outputs = outputs + [create_instance_group_output(bastion_name)]
    else:
        outputs = outputs + [create_bastion_ip_output(bastion_name)]

    return {
        'resources':
            resources,
        'outputs':
            outputs
    }
