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
                'appautoscalegroup': context.properties['uniqueString'],
                'application': context.properties['application'],
                'cost': context.properties['cost'],
                'environment': context.properties['environment'],
                'group': context.properties['group'],
                'owner': context.properties['owner']
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
                    'sourceImage': 'projects/ubuntu-os-cloud/global/images/family/ubuntu-1604-lts'
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
  }]

  return {'resources': resources}
