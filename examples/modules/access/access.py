# Copyright 2021 F5 Networks All rights reserved.
#
# Version 2.2.0.0

# pylint: disable=W,C,R,duplicate-code,line-too-long

"""Creates the access"""
COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'


def generate_name(prefix, suffix, exclude_chars=None):
    """ Generate unique name """
    if exclude_chars is None:
        return prefix + "-" + suffix
    for character in exclude_chars:
        prefix = prefix.replace(character, '')
        suffix = suffix.replace(character, '')

    if '-' in exclude_chars:
        return prefix + suffix
    return prefix + "-" + suffix

def create_service_account(context, service_account_name):
    """ Create service account resource """
    optional_properties = [
        'accountId'
    ]
    properties = {}
    properties.update({
        'accountId': ''.join([context.properties['uniqueString'], '-admin']),
        'displayName': service_account_name
    })
    for config in context.properties:
        properties.update(
            {
                p: context.properties[p]
                for p in optional_properties
                if p in config
            }
        )
    service_account = {
        'name': service_account_name,
        'type': 'iam.v1.serviceAccount',
        'properties': properties
    }
    return service_account

def create_custom_role(context, role_name):
    """ Create custom role resource """
    optional_properties = [
        'description'
    ]
    properties = {}
    properties.update({
        'parent': ''.join(['projects/', context.env['project']]),
        'roleId': role_name,
        'role': {
            'title': role_name,
            'description': 'A custom role for the deployment',
            'includedPermissions': create_role_permissions(context, context.properties['solutionType'])
        }
    })
    for config in context.properties:
        properties.update(
            {
                p: context.properties[p]
                for p in optional_properties
                if p in config
            }
        )
    custom_role = {
        'name': role_name,
        'type': 'gcp-types/iam-v1:projects.roles',
        'properties': properties
    }
    return custom_role

def create_role_permissions(context, solution_type):
    """ Create permissions list """
    # Build role permissions based on solutionType
    if solution_type in ['standard', 'secret', 'storage',
                         'remoteLogging', 'failover']:
        included_permissions = [
            'compute.instances.get',
            'compute.instances.list',
            'compute.targetInstances.get',
            'compute.targetInstances.list',
            'compute.forwardingRules.get',
            'compute.forwardingRules.list',          
            'compute.globalOperations.get',
            'logging.logEntries.create',
            'monitoring.timeSeries.create',
            'monitoring.metricDescriptors.create',
            'monitoring.metricDescriptors.get',
            'monitoring.metricDescriptors.list',
            'monitoring.monitoredResourceDescriptors.get',
            'monitoring.monitoredResourceDescriptors.list',
            'resourcemanager.projects.get'
        ]
    if solution_type in ['secret', 'failover']:
        included_permissions = included_permissions + [          
            'secretmanager.versions.get',
            'secretmanager.versions.list',
            'secretmanager.versions.access'
        ]
    if solution_type in ['storage', 'remoteLogging', 'failover']:
        included_permissions = included_permissions + [
            'storage.objects.get',
            'storage.objects.create',
            'storage.objects.update',
            'storage.objects.list',
            'storage.objects.delete',
            'storage.buckets.get',
            'storage.buckets.update',
            'storage.buckets.list'
        ]
    if solution_type in ['failover']:
        included_permissions = included_permissions + [
            'compute.routes.get',
            'compute.routes.list',
            'compute.routes.create',
            'compute.routes.delete',
            'compute.targetInstances.use',
            'compute.forwardingRules.setTarget',
            'compute.instances.updateNetworkInterface',
            'compute.networks.updatePolicy'
        ]
    if solution_type in ['custom']:
        included_permissions = context.properties['includedPermissions'].split()
    return included_permissions

def create_binding(context, service_account_name, role_name):
    """ Bind role to service account """
    properties = {}
    properties.update({
        'resource': context.env['project'],
        'role': 'projects/' + context.env['project'] + '/roles/' + role_name,
        'member': 'serviceAccount:$(ref.' + service_account_name + '.email)'
    })
    binding = {
        'name': ''.join([context.properties['uniqueString'], '-bigip-bind-iam-policy']),
        'type': 'gcp-types/cloudresourcemanager-v1:virtual.projects.iamMemberBinding',
        'properties': properties
    }
    return binding

def generate_config(context):
    """Entry point for the deployment resources."""
    service_account_name = generate_name(context.properties['uniqueString'],
                                         'bigip-sa')
    role_name = generate_name(context.properties['uniqueString'],
                              'bigipaccessrole',
                              ['-'])
    resources = [create_service_account(context, service_account_name)] + \
                    [create_custom_role(context, role_name)] + \
                        [create_binding(context, service_account_name, role_name)]
    outputs = [
        {
            'name': 'serviceAccountEmail',
            'value': '$(ref.' + service_account_name + '.email)'
        },
        {
            'name': 'customRoleName',
            'value': '$(ref.' + role_name + '.name)'
        },
        {
            'name': 'customRolePermissions',
            'value': '$(ref.' + role_name + '.includedPermissions)'
        }
    ]

    return {'resources': resources, 'outputs': outputs}
