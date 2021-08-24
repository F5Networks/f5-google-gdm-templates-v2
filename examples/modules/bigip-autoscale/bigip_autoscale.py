# Copyright 2021 F5 Networks All rights reserved.
#
# Version 0.1.0

# pylint: disable=W,C,R,duplicate-code,line-too-long

"""Creates the application"""
COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'


def generate_name(prefix, suffix):
    """ Generate unique name """
    return prefix + "-" + suffix


def create_instance_template(context, instance_template_name):
    """ Create autoscale instance template """
    instance_template = {
        'name': instance_template_name,
        'type': 'compute.v1.instanceTemplate',
        'properties': {
            'properties': {
                'tags': {
                    'items': [context.properties['uniqueString'] + '-mgmt-fw', context.properties['uniqueString'] + '-app-vip-fw']
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
                    'subnetwork': context.properties['subnetSelfLink']
                }],
                'labels': {
                    'application': context.properties['application'],
                    'cost': context.properties['cost'],
                    'environment': context.properties['environment'],
                    'group': context.properties['group'],
                    'owner': context.properties['owner']
                },
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
                                            'exec 2>&1\n',
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
    }
    if not context.properties['update']:
        instance_template['metadata'] = {
            'dependsOn': [
                context.properties['networkSelfLink'].split("/").pop(),
                context.properties['subnetSelfLink'].split("/").pop(),
                context.properties['uniqueString'] + '-bigip-sa'
            ]
        }
    if context.properties['provisionPublicIp']:
        instance_template['properties']['properties']['networkInterfaces'][0]['accessConfigs'] = \
            [{'name': 'Management NAT','type': 'ONE_TO_ONE_NAT'}]
    return instance_template


def create_instance_group(context, instance_template_name):
    """Create autoscale instance group."""
    instance_group = {
        'name': context.properties['uniqueString'] + '-bigip-igm',
        'type': 'compute.beta.instanceGroupManager',
        'properties': {
            'baseInstanceName': context.properties['uniqueString'] + '-bigip-vm',
            'instanceTemplate': '$(ref.' + instance_template_name + '.selfLink)',
            'targetPools': ['$(ref.' + context.properties['uniqueString'] + '-bigip-tp.selfLink)'],
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
    """Create autoscaler."""
    autoscaler = {
        'name': context.properties['uniqueString'] + '-bigip-as',
        'type': 'compute.v1.autoscalers',
        'properties': {
            'zone': context.properties['availabilityZone'],
            'target': '$(ref.' + context.properties['uniqueString'] + '-bigip-igm.selfLink)',
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
    """Create health check."""
    applicaton_port = str(context.properties['applicationVipPort'])
    applicaton_port = applicaton_port.split()[0]
    if source == "internal":
        health_check = {
            'name': context.properties['uniqueString'] + '-' + source + '-hc',
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
            'name': context.properties['uniqueString'] + '-' + source + '-hc',
            'type': 'compute.v1.httpHealthCheck',
            'properties': {
                'port': int(applicaton_port)
            }
        }

    return health_check

def create_target_pool(context):
    """ Create target pool """
    target_pool = {
        'name': context.properties['uniqueString'] + '-bigip-tp',
        'type': 'compute.v1.targetPool',
        'properties': {
            'region': context.properties['region'],
            'sessionAffinity': 'CLIENT_IP',
            'healthChecks': ['$(ref.' + context.properties['uniqueString'] + '-external-hc.selfLink)'],
        }
    }
    return target_pool

def create_target_pool_outputs(context):
    """ Create target pool outputs """
    target_pool = {
        'name': 'targetPool',
        'resourceName': context.properties['uniqueString'] + '-bigip-tp',
        'value': '$(ref.' + context.properties['uniqueString'] + '-bigip-tp.selfLink)'
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
                          context.properties['uniqueString'],
                          '-bigip-igm'
                          ])
    }
    return instance_group

def generate_config(context):
    """ Entry point for the deployment resources. """

    name = context.properties.get('name') or \
           context.env['name']
    bigip_autoscale_deployment_name = generate_name(context.properties['uniqueString'], name)
    instance_template_name = context.properties['uniqueString'] + \
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
