# Copyright 2021 F5 Networks All rights reserved.
#
# Version 2.2.0.0

# pylint: disable=W,C,R,duplicate-code,line-too-long

COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'


def generate_name(prefix, suffix):
    """Generate unique name."""
    return prefix + "-" + suffix


def populate_properties(context, required_properties, optional_properties):
    properties = {}
    properties.update(
        {
            p: context[p]
            for p in required_properties
        }
    )

    properties.update(
        {
            p: context[p]
            for p in optional_properties
            if p in context.keys()
        }
    )
    return properties


def create_instance(context, instance):
    """ Create standalone application instance."""
    # Build instance property lists
    required_properties = ['zone']
    optional_properties = [
        'advancedMachineFeatures',
        'canIpForward',
        'confidentialInstanceConfig',
        'description',
        'disks',
        'guestAccelerators',
        'labels',
        'machineType',
        'minCpuPlatform',
        'privateIpv6GoogleAccess',
        'reservationAffinity',
        'resourcePolicies',
        'scheduling',
        'serviceAccounts',
        'shieldedInstanceConfig',
        'tags'
    ]
    # Setup Variables
    prefix = context.properties['uniqueString']
    name = instance.get('name') or context.env['name'] if 'name' in instance or 'name' in context.env else 'demo'
    instance_name = generate_name(prefix, name)
    application = context.properties['application'] if 'application' in context.properties else 'demo'
    cost = context.properties['cost'] if 'cost' in context.properties else 'demo'
    environment =  context.properties['environment'] if 'environment' in context.properties else 'demo'
    group = context.properties['group'] if 'group' in context.properties else 'demo'
    owner = context.properties['owner'] if 'owner' in context.properties else 'demo'
    properties = {}

    # Setup Defaults - property updated to given value when property exists in config
    properties.update({
            'description': 'Standalone POC Application.',
            'disks': [{
                'deviceName': 'boot',
                'type': 'PERSISTENT',
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': ''.join([COMPUTE_URL_BASE, 'projects/',
                                    'centos-cloud/global/images/family/centos-7'])
                }
            }],
            'hostname': ''.join([instance_name,
            '.c.', context.env['project'], '.internal']),
            'labels': {
                'appautoscalegroup': context.properties['uniqueString'],
                'failovergroup': context.properties['uniqueString'],
                'application': application,
                'cost': cost,
                'environment': environment,
                'group': group,
                'owner': owner
            },
            'machineType': ''.join([COMPUTE_URL_BASE, 'projects/', context.env['project'],
            '/zones/', instance['zone'], '/machineTypes/',
            context.properties['instanceType']]),
            'metadata': {
                'items': [{
                    'key': 'startup-script',
                    'value': ''.join(['#!/bin/bash\n',
                               'yum -y install docker\n',
                               'service docker start\n',
                               'docker run --name f5demo -p 80:80 -p 443:443 -d ',
                                context.properties['appContainerName']])
                }]
            },
            'name': instance_name,
            'networkInterfaces': create_nics(instance),
            'tags': {
                'items': [generate_name(prefix, 'app-int-fw'), generate_name(prefix, 'app-vip-fw')]
            },
            'zone': instance['zone']
    })
    properties.update(populate_properties(instance, required_properties, optional_properties))
    instance = {
            'name': instance_name,
            'type': 'compute.v1.instance',
            'properties': properties
    }
    return instance


def create_nics(context):
    """ Create interface configuration for instance """
    # Build interface properties lists
    required_properties = ['network', 'subnetwork']
    optional_properties = [
        'description',
        'networkIP',
        'ipv6Address',
        'networkTier',
        'stackType',
        'queueCount',
        'nicType',
        'aliasIpRanges',
        'ipv6AccessConfigs',
        'accessConfigs',
        'name'
    ]
    network_interfaces = []
    for network in context.get('networkInterfaces', []):
        # Build interface configuration
        network_interfaces.append(populate_properties(network, required_properties, optional_properties))
    return network_interfaces


def create_instance_template(context, instance_templates):
    """Create autoscale instance template."""
    # Build instance property lists
    required_properties = []
    optional_properties = [
        'advancedMachineFeatures',
        'canIpForward',
        'confidentialInstanceConfig',
        'deletionProtection',
        'description',
        'disks',
        'displayDevice',
        'guestAccelerators',
        'hostname',
        'labels',
        'machineType',
        'minCpuPlatform',
        'privateIpv6GoogleAccess',
        'reservationAffinity',
        'resourcePolicies',
        'scheduling',
        'serviceAccounts',
        'shieldedInstanceConfig',
        'shieldedInstanceIntegrityPolicy',
        'tags'
    ]
    # Setup Variables
    prefix = context.properties['uniqueString']
    name = instance_templates.get('name') or context.env['name'] if 'name' in instance_templates or 'name' in context.env else 'demo'
    instance_template_name = generate_name(prefix, name + '-v' + str(context.properties['instanceTemplateVersion']))
    application = context.properties['application'] if 'application' in context.properties else 'demo'
    cost = context.properties['cost'] if 'cost' in context.properties else 'demo'
    environment =  context.properties['environment'] if 'environment' in context.properties else 'demo'
    group = context.properties['group'] if 'group' in context.properties else 'demo'
    owner = context.properties['owner'] if 'owner' in context.properties else 'demo'
    properties = {}

    # Setup Defaults - property updated to given value when property exists in config
    properties.update({
            'labels': {
                'appautoscalegroup': prefix,
                'failovergroup': prefix,
                'application': application,
                'cost': cost,
                'environment': environment,
                'group': group,
                'owner': owner
            },
            'tags': {
                'items': [generate_name(prefix, 'app-int-fw'), generate_name(prefix, 'app-vip-fw')]
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
            'networkInterfaces': create_nics(instance_templates),
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
        })
    properties.update(populate_properties(instance_templates, required_properties, optional_properties))
    instance_template_config = {
            'name': instance_template_name,
            'type': 'compute.v1.instanceTemplates',
            'properties': {
                'description': 'F5 demo Application',
                'name': instance_template_name,
                'properties': properties,
            }
    }
    return instance_template_config


def create_instance_group(context, instance_group_managers):
    """Create autoscale instance group."""
    # Build instance property lists
    required_properties = ['zone']
    optional_properties = [
        'autoHealingPolicies',
        'baseInstanceName',
        'description',
        'distributionPolicy',
        'instanceTemplate',
        'namedPorts',
        'statefulPolicy',
        'targetPools',
        'targetSize',
        'updatePolicy',
        'versions'
    ]

    # Setup Variables
    prefix = context.properties['uniqueString']
    name = instance_group_managers.get('name') or context.env['name'] if 'name' in instance_group_managers or 'name' in context.env else 'demo'
    base_instance_name = generate_name(prefix, name + '-vm')
    instance_template_name = generate_name(prefix, name + '-v' + str(context.properties['instanceTemplateVersion']))
    instance_group_manager_name = generate_name(prefix, name + '-igm')
    properties = {}

    # Setup Defaults - property updated to given value when property exists in config

    properties.update({
        'baseInstanceName': base_instance_name,
        'instanceTemplate': '$(ref.' + instance_template_name + '.selfLink)',
        'name': instance_group_manager_name,
        'targetSize': 2,
        'updatePolicy': {
            'minimalAction': 'REPLACE',
            'type': 'PROACTIVE'
        }
    })
    properties.update(populate_properties(instance_group_managers, required_properties, optional_properties))
    instance_group_manager_config = {
        'name': instance_group_manager_name,
        'type': 'compute.beta.instanceGroupManager',
        'properties': properties
    }
    return instance_group_manager_config


def create_autoscaler(context, autoscalers):
    """Create autoscaler."""
    # Build instance property lists
    required_properties = ['zone']
    optional_properties = [
        'autoscalingPolicy',
        'description',
        'target'
    ]
    # Setup Variables
    prefix = context.properties['uniqueString']
    name = autoscalers.get('name') or context.env['name'] if 'name' in autoscalers or 'name' in context.env else 'demo'
    autoscaler_name = generate_name(prefix, name + '-as')
    instance_group_manager_name = generate_name(prefix, name + '-igm')
    properties = {}

    # Setup Defaults - property updated to given value when property exists in config
    properties.update({
        'autoscalingPolicy': {
            "minNumReplicas": 1,
            'maxNumReplicas': 8,
            'cpuUtilization': {
                'utilizationTarget': 0.8
            },
            'coolDownPeriodSec': 60
        },
        'name': autoscaler_name,
        'target': '$(ref.' + instance_group_manager_name + '.selfLink)',
    })
    properties.update(populate_properties(autoscalers, required_properties, optional_properties))
    autoscaler_config = {
        'name': autoscaler_name,
        'type': 'compute.v1.autoscalers',
        'properties': properties
    }
    return autoscaler_config


def create_application_ip_output(context, instance):
    """Create instance app IP output."""
    # Setup Variables
    prefix = context.properties['uniqueString']
    name = instance.get('name') or context.env['name'] if 'name' in instance or 'name' in context.env else 'demo'
    instance_name = generate_name(prefix, name)
    application_ip = {
        'name': 'applicationIp',
        'value': '$(ref.{}.networkInterfaces[0].'
                 'accessConfigs[0].natIP)'.format(instance_name)
    }
    return application_ip


def create_instance_group_output(context, instance_group_managers):
    """Create instance group output."""
    prefix = context.properties['uniqueString']
    name = instance_group_managers.get('name') or context.env['name'] if 'name' in instance_group_managers or 'name' in context.env else 'demo'
    instance_group_manager_name = generate_name(prefix, name + '-igm')
    instance_group = {
        'name': 'instanceGroup',
        'value': '$(ref.' + instance_group_manager_name + '.selfLink)'
    }
    return instance_group


def generate_config(context):
    """Entry point for the deployment resources."""
    name = context.properties['name'] if 'name' in context.properties else 'demo'
    resources = []
    for autoscaler in context.properties.get('autoscalers', []):
        resources.append(create_autoscaler(context, autoscaler))
    for instance in context.properties.get('instances', []):
        resources.append(create_instance(context, instance))
    for instanceGroupManager in context.properties.get('instanceGroupManagers', []):
        resources.append(create_instance_group(context, instanceGroupManager))
    for instanceTemplate in context.properties.get('instanceTemplates', []):
        resources.append(create_instance_template(context, instanceTemplate))

    outputs = [
        {
            'name': 'applicationName',
            'value': generate_name(context.properties['uniqueString'], name)
        }
    ]

    for instanceGroupManager in context.properties.get('instanceGroupManagers', []):
        outputs = outputs + [create_instance_group_output(context, instanceGroupManager)]
    for instance in context.properties.get('instances', []):
        outputs = outputs + [create_application_ip_output(context, instance)]

    return {
        'resources':
            resources,
        'outputs':
            outputs
    }
