# Copyright 2021 F5 Networks All rights reserved.
#
# Version 2.2.0.0

# pylint: disable=W,C,R,duplicate-code,line-too-long

"""Creates the application."""
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


def create_instance_template(context, instance_template):
    """Create autoscale instance template."""
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
    name = instance_template.get('name') or context.env['name'] if 'name' in instance_template or 'name' in context.env else 'template'
    instance_template_name = generate_name(prefix, name + '-v' + str(context.properties['instanceTemplateVersion']))
    application = context.properties['application'] if 'application' in context.properties else 'f5app'
    cost = context.properties['cost'] if 'cost' in context.properties else 'f5cost'
    environment =  context.properties['environment'] if 'environment' in context.properties else 'f5env'
    group = context.properties['group'] if 'group' in context.properties else 'f5group'
    owner = context.properties['owner'] if 'owner' in context.properties else 'f5owner'
    properties = {}

    # Setup Defaults - property updated to given value when property exists in config
    properties.update({
        'labels': {
            'application': application,
            'cost': cost,
            'environment': environment,
            'group': group,
            'owner': owner
        },
        'tags': {
            'items': [generate_name(prefix, 'mgmt-fw'), generate_name(prefix, 'app-vip-fw')]
        },
        'machineType': context.properties['instanceType'],
        'serviceAccounts': [{
            'email': context.properties['serviceAccountEmail'],
            'scopes': ['https://www.googleapis.com/auth/compute', 'https://www.googleapis.com/auth/devstorage.read_write', "https://www.googleapis.com/auth/cloud-platform"]
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
                                    'echo $(date +"%Y-%m-%dT%H:%M:%S.%3NZ") : Startup Script Start',
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
                                    'bash "/var/config/rest/downloads/${PACKAGE_URL##*/}" -- \'--cloud gcp --telemetry-params templateName:v2.2.0.0/examples/modules/bigip-autoscale/bigip_autoscale.py\'',
                                    '',
                                    '# Execute Runtime-init',
                                    'bash "/usr/local/bin/f5-bigip-runtime-init" --config-file /config/cloud/runtime-init.conf',
                                    'echo $(date +"%Y-%m-%dT%H:%M:%S.%3NZ") : Startup Script Finish'
                                    ])
            },
            {
                'key': 'unique-string',
                'value': prefix
            },
            {
                'key': 'region',
                'value': context.properties['region']
            }]
        }
    })

    properties.update(populate_properties(instance_template, required_properties, optional_properties))

    if context.properties['provisionPublicIp']:
        network_interfaces = properties['networkInterfaces'].copy()
        network_interfaces[0].update({'accessConfigs': [{'name': 'Management NAT', 'type': 'ONE_TO_ONE_NAT'}]})
        properties.update({'networkInterfaces': network_interfaces})

    instance_template_config = {
            'name': instance_template_name,
            'type': 'compute.v1.instanceTemplates',
            'properties': {
                'description': 'BIG-IP Autoscale Solution',
                'name': instance_template_name,
                'properties': properties,
            }
    }
    return instance_template_config


def create_instance_group(context, instance_group_manager):
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
    name = instance_group_manager.get('name') or context.env['name'] if 'name' in instance_group_manager or 'name' in context.env else 'bigip'
    base_instance_name = generate_name(prefix, name + '-vm')
    instance_template_name = generate_name(prefix, name + '-v' + str(context.properties['instanceTemplateVersion']))
    instance_group_manager_name = generate_name(prefix, name + '-igm')
    target_pool_name = generate_name(prefix, name + '-tp')
    properties = {}


    # Setup Defaults - property updated to given value when property exists in config
    properties.update({
        'baseInstanceName': base_instance_name,
        'instanceTemplate': '$(ref.' + instance_template_name + '.selfLink)',
        'name': instance_group_manager_name,
        'targetPools': ['$(ref.' + target_pool_name + '.selfLink)'],
        'targetSize': 2,
        'updatePolicy': {
            'minimalAction': 'REPLACE',
            'type': 'PROACTIVE'
        }
    })
    properties.update(populate_properties(instance_group_manager, required_properties, optional_properties))
    instance_group_manager_config = {
        'name': instance_group_manager_name,
        'type': 'compute.beta.instanceGroupManager',
        'properties': properties
    }
    return instance_group_manager_config


def create_autoscaler(context, autoscaler):
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
    name = autoscaler.get('name') or context.env['name'] if 'name' in autoscaler or 'name' in context.env else 'bigip'
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

    properties.update(populate_properties(autoscaler, required_properties, optional_properties))
    autoscaler_config = {
        'name': autoscaler_name,
        'type': 'compute.v1.autoscalers',
        'properties': properties
    }
    return autoscaler_config


def create_health_check(context, health_check, source):
    """Create health check."""
    # Build health check property list
    required_properties = []
    optional_properties = [
        'description',
        'checkIntervalSec',
        'timeoutSec',
        'unhealthyThreshold',
        'healthyThreshold',
        'tcpHealthCheck',
        'sslHealthCheck',
        'httpHealthCheck',
        'httpsHealthCheck',
        'http2HealthCheck',
        'grpcHealthCheck',
        'logConfig',
        'type'
    ]

    # Setup Variables
    prefix = context.properties['uniqueString']
    health_check_name = generate_name(prefix, str(source + '-hc'))
    properties = {}

    # Setup Defaults - property updated to given value when property exists in config
    properties.update({
        'checkIntervalSec': 5,
        'timeoutSec': 5,
        'name': health_check_name
    })

    # Populate the properties and create the config object
    properties.update(populate_properties(health_check, required_properties, optional_properties))
    if source == "internal":
        health_check_config = {
            'name': health_check_name,
            'type': 'compute.v1.healthCheck',
            'properties': properties
        }
    else:
        health_check_config = {
            'name': health_check_name,
            'type': 'compute.v1.httpHealthCheck',
            'properties': properties
        }

    return health_check_config


def create_target_pool(context, target_pool):
    """Create target pool."""
    # Build instance property lists
    required_properties = ['region']
    optional_properties = [
        'sessionAffinity',
        'healthChecks'
    ]

    # Setup Variables
    prefix = context.properties['uniqueString']
    name = target_pool.get('name') or context.env['name'] if 'name' in target_pool or 'name' in context.env else 'bigip'
    target_pool_name = generate_name(prefix, name + '-tp')
    health_check_name = generate_name(prefix, 'external-hc')
    properties = {}


    # Setup Defaults - property updated to given value when property exists in config
    properties.update({
        'sessionAffinity': 'CLIENT_IP',
        'healthChecks': ['$(ref.' + health_check_name + '.selfLink)'],
        'name': target_pool_name,
    })

    properties.update(populate_properties(target_pool, required_properties, optional_properties))
    target_pool_config = {
        'name': target_pool_name,
        'type': 'compute.v1.targetPool',
        'properties': properties
    }
    return target_pool_config


def create_target_pool_outputs(context, target_pool):
    """Create target pool outputs."""
    prefix = context.properties['uniqueString']
    name = target_pool.get('name') or context.env['name'] if 'name' in target_pool or 'name' in context.env else 'bigip'
    target_pool_name = generate_name(prefix, name + '-tp')
    target_pool = {
        'name': 'targetPool',
        'resourceName': target_pool_name,
        'value': '$(ref.' + target_pool_name + '.selfLink)'
    }
    return target_pool


def create_instance_group_output(context, instance_group_manager):
    """Create instance group output."""
    prefix = context.properties['uniqueString']
    name = instance_group_manager.get('name') or context.env['name'] if 'name' in instance_group_manager or 'name' in context.env else 'bigip'
    instance_group_manager_name = generate_name(prefix, name + '-igm')
    instance_group = {
        'name': 'instanceGroupName',
        'value': instance_group_manager_name
    }
    return instance_group


def generate_config(context):
    """Entry point for the deployment resources."""
    prefix = context.properties['uniqueString']
    name = context.properties.get('name') or \
           context.env['name']
    bigip_autoscale_deployment_name = generate_name(prefix, name)

    resources = []
    for autoscaler in context.properties.get('autoscalers', []):
        resources.append(create_autoscaler(context, autoscaler))
    for targetPool in context.properties.get('targetPools', []):
        resources.append(create_target_pool(context, targetPool))
    for healthCheck in context.properties.get('healthChecks', []):
        resources.append(create_health_check(context, healthCheck, 'external'))
    for instanceGroupManager in context.properties.get('instanceGroupManagers', []):
        resources.append(create_instance_group(context, instanceGroupManager))
    for instanceTemplate in context.properties.get('instanceTemplates', []):
        resources.append(create_instance_template(context, instanceTemplate))

    outputs = [
        {
            'name': 'bigipAutoscaleName',
            'value': bigip_autoscale_deployment_name
        }
    ]

    for instanceGroupManager in context.properties.get('instanceGroupManagers', []):
        outputs = outputs + [create_instance_group_output(context, instanceGroupManager)]
    for targetPool in context.properties.get('targetPools', []):
        outputs = outputs + [create_target_pool_outputs(context, targetPool)]

    return {
        'resources':
            resources,
        'outputs':
            outputs
    }
