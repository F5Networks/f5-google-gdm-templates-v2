# Copyright 2021 F5 Networks All rights reserved.
#
# Version 0.1.0

# pylint: disable=W,C,R

COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'

def generate_config(context):
  """Generate instance template resource configuration."""

  access_configs = []
  if context.properties['provisionPublicIp']:
    access_configs = [{'name': 'Management NAT','type': 'ONE_TO_ONE_NAT'}]

  resources = [{
    'name': context.env['name'],
    'type': 'compute.v1.instanceTemplate',
    'properties': {
        'properties': {
            'tags': {
                'items': ['mgmtfw-'+ context.properties['uniqueString'], 'appfwvip-'+ context.properties['uniqueString']]
            },
            'machineType': context.properties['instanceType'],
            'serviceAccounts': [{
                'email': context.properties['serviceAccountEmail'],
                'scopes': ['https://www.googleapis.com/auth/compute','https://www.googleapis.com/auth/devstorage.read_write']
            }],
            'disks': [{
                'deviceName': 'boot',
                'type': 'PERSISTENT',
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': ''.join([COMPUTE_URL_BASE,
                                            'projects/f5-7626-networks-public',
                                            '/global/images/',
                                            context.properties['imageName'],
                                            ])
                }
            }],
            'networkInterfaces': [{
                'network': context.properties['networkSelfLink'],
                'subnetwork': context.properties['subnetSelfLink'],
                'accessConfigs': access_configs
            }],
            'metadata': {
                'items': [{
                    'key': 'startup-script',
                    'value': '\n'.join(['#!/bin/bash',
                                        '# Log to local file and serial console',
                                        'mkdir -p /var/log/cloud /config/cloud /var/config/rest/downloads',
                                        'LOG_FILE=/var/log/cloud/startup-script.log',
                                        'echo \'Initializing Runtime Init\'',
                                        'npipe=/tmp/$$.tmp',
                                        'trap \'rm -f $npipe\' EXIT',
                                        'mknod $npipe p',
                                        'tee <$npipe -a ${LOG_FILE} /dev/ttyS0 &',
                                        'exec 1>&-',
                                        'exec 1>$npipe',
                                        'exec 2>&1'
                                        'echo $(date +"%Y-%m-%dT%H:%M:%S.%3NZ") : Startup Script Start' ,
                                        '# Optional optimizations required as early as possible in boot sequence before MCDP starts up.',
                                        '/usr/bin/setdb provision.extramb 1000',
                                        '/usr/bin/setdb restjavad.useextramb true',
                                        '! grep -q \'provision asm\' /config/bigip_base.conf && echo \'sys provision asm { level nominal }\' >> /config/bigip_base.conf',
                                        '',
                                        '# VARS FROM TEMPLATE',
                                        'PACKAGE_URL=' + context.properties['bigIpRuntimeInitPackageUrl'],
                                        '',
                                        'RUNTIME_CONFIG=' + context.properties['bigIpRuntimeInitConfig'],
                                        '',
                                        '# Download or render f5-bigip-runtime-init config',
                                        'if [[ "${RUNTIME_CONFIG}" =~ ^http.* ]]; then',
                                        ' for i in {1..30}; do',
                                        '     curl -sfv --retry 1 --connect-timeout 5 -L "${RUNTIME_CONFIG}" -o /config/cloud/runtime-init.conf && break || sleep 10',
                                        ' done',
                                        'else',
                                        ' printf %s\n "${RUNTIME_CONFIG}" | jq .  > /config/cloud/runtime-init.conf',
                                        'fi',
                                        '# Download and install f5-bigip-runtime-init package',
                                        'for i in {1..30}; do',
                                        'curl -fv --retry 1 --connect-timeout 5 -L "${PACKAGE_URL}" -o "/var/config/rest/downloads/${PACKAGE_URL##*/}" && break || sleep 10',
                                        'done',
                                        '',
                                        '# Run',
                                        'bash "/var/config/rest/downloads/${PACKAGE_URL##*/}" -- \'--cloud gcp\'',
                                        '',
                                        '# Execute Runtime-init',
                                        'bash "/usr/local/bin/f5-bigip-runtime-init" --config-file /config/cloud/runtime-init.conf',
                                        'echo $(date +"%Y-%m-%dT%H:%M:%S.%3NZ") : Startup Script Finish'
                                        ])
                },
                {
                    'key': 'unique-string',
                    'value': context.properties['uniqueString']
                },
                {
                    'key': 'region',
                    'value': context.properties['region']
                }]
            }
        }
    }
  }]

  return {'resources': resources}