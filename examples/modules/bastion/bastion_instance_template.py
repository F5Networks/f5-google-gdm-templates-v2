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
                    'value': ''.join([
                        '#!/bin/bash\n',
                        'echo "***** Welcome to Bastion Host *****" > /etc/ssh_banner',
                        'echo "[INFO] Installing banner ..."',
                        'echo -e "\n Banner /etc/ssh_banner" >> /etc/ssh/sshd_config',
                        'echo "[INFO] Configuring TCP forwarding"',
                        'awk \'!/AllowTcpForwarding/\' /etc/ssh/sshd_config > temp && mv temp /etc/ssh/sshd_config',
                        'echo "AllowTcpForwarding yes" >> /etc/ssh/sshd_config',
                        'echo "[INFO] Configuring X11 forwarding"',
                        'awk \'!/AllowTcpForwarding/\' /etc/ssh/sshd_config > temp && mv temp /etc/ssh/sshd_config',
                        'echo "AllowTcpForwarding yes" >> /etc/ssh/sshd_config'
                                      ])
                }]
            }
        }
    }
  }]

  return {'resources': resources}
