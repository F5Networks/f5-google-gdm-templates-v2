# Copyright 2021 F5 Networks All rights reserved.
#
# Version 0.1.0

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


def create_custom_role(context, role_name, solution_type):
    """ Build custom role """

    if solution_type in ['standard', 'secret', 'storage',
                         'remoteLogging', 'failover']:
        included_permissions = [
            'compute.instances.create',
            'compute.instances.get',
            'compute.instances.list',
            'compute.targetInstances.get',
            'compute.targetInstances.list',
            'compute.targetInstances.use',
            'compute.routes.get',
            'compute.routes.list',
            'compute.routes.create',
            'compute.routes.delete',
            'compute.forwardingRules.get',
            'compute.forwardingRules.list',
            'compute.forwardingRules.setTarget',
            'compute.instances.updateNetworkInterface',
            'compute.networks.updatePolicy',
            'compute.globalOperations.get'
        ]
    if solution_type in ['secret', 'remoteLogging', 'failover']:
        included_permissions.append(
            'resourcemanager.projects.get',
            'resourcemanager.projects.list',
            'secretmanager.versions.add',
            'secretmanager.versions.destroy',
            'secretmanager.versions.disable',
            'secretmanager.versions.enable',
            'secretmanager.versions.get',
            'secretmanager.versions.list',
            'secretmanager.versions.access'
        )
    if solution_type in ['storage', 'remoteLogging', 'failover']:
        included_permissions.append(
            'storage.objects.get',
            'storage.objects.create',
            'storage.objects.update',
            'storage.objects.list',
            'storage.objects.delete',
            'storage.buckets.get',
            'storage.buckets.create',
            'storage.buckets.update',
            'storage.buckets.delete',
            'storage.buckets.list'
        )

    custom_role = {
        'name': role_name,
        'type': 'gcp-types/iam-v1:projects.roles',
        'properties': {
            'parent': ''.join(['projects/', context.env['project']]),
            'roleId': role_name,
            'role': {
                'title': role_name,
                'description': 'A custom role for the deployment',
                'includedPermissions': included_permissions
            }
        }
    }
    return custom_role


def generate_config(context):
    """ Entry point for the deployment resources. """

    name = context.properties.get('name') or \
        context.env['name']
    service_account_name = generate_name(context.properties['uniqueString'],
                                         name)
    role_name = generate_name('BigIPAccessRole',
                              context.properties['uniqueString'],
                              ['-'])

    solution_type = context.properties['solutionType']

    # storage_name = context.properties.get(
    #     'storageName',
    #     False
    # )

    # secret_id = context.properties.get(
    #     'secretId',
    #     False
    # )

    resources = [
        create_custom_role(context, role_name, solution_type)
    ]

    resources.append(
        {
            'name': service_account_name,
            'type': 'iam.v1.serviceAccount',
            'properties': {
                'accountId': ''.join([context.env['deployment'], '-admin']),
                'displayName': service_account_name
            },
            'accessControl': {
                'gcpIamPolicy': {
                    'bindings': {
                        'role': '$(ref.' + role_name + '.name)',
                        'members': [''.join(['serviceAccount:',
                                             context.env['deployment'],
                                             '-admin',
                                             '@', context.env['project'],
                                             '.iam.gserviceaccount.com'])]
                    }
                }
            },
            'metadata': {
                'dependsOn': [role_name]
            }
        }
    )

    return {
        'resources': resources,
        'outputs':
            [
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
    }
