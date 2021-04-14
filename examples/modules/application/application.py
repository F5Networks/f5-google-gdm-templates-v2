# Copyright 2021 F5 Networks All rights reserved.
#
# Version 0.1.0

"""Creates the application"""
COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'


def generate_name(prefix, suffix):
    """ Generate unique name """
    return prefix + "-" + suffix


def generate_config(context):
    """ Entry point for the deployment resources. """

    name = context.properties.get('name') or \
        context.env['name']
    application_name = generate_name(context.properties['uniqueString'], name)

    resources = [
        {
            'name': application_name,
            'type': 'compute.v1.instance',
            'properties': {
                'zone': context.properties['availabilityZone'],
                'hostname': context.properties['hostname'],
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
                                                'images/centos-7-v20210401'])
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
        }]
    return {
        'resources':
            resources,
        'outputs':
            [
                {
                    'name': 'applicationName',
                    'value': application_name
                },
                {
                    'name': 'applicationIp',
                    'value': '$(ref.{}.networkInterfaces[0].'
                             'accessConfigs[0].natIP)'.format(application_name)
                }
            ]

    }
