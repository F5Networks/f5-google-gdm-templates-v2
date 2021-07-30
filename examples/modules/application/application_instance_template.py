# Copyright 2021 F5 Networks All rights reserved.
#
# Version 0.1.0

# pylint: disable=W,C,R

COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'

def generate_config(context):
  """Generate instance template resource configuration."""

  resources = [{
    'name': context.env['name'],
    'type': 'compute.v1.instanceTemplate',
    'properties': {
        'properties': {
            'labels': {
                'appautoscalegroup': context.properties['uniqueString']
            },
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
                                            'images/family/centos-7'])
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
  }]

  return {'resources': resources}