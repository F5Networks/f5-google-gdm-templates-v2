"""Creates the access."""

import sys
import json

with open('foundPermissions.json') as data_file:
    data = data_file.read()
    found_permissions = json.loads(data)
    found_permissions = found_permissions['includedPermissions']

if sys.argv[1] in ['standard', 'secret', 'storage',
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
if sys.argv[1] in ['secret', 'remoteLogging', 'failover']:
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
if sys.argv[1] in ['storage', 'remoteLogging', 'failover']:
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

set_included_permissions = set(included_permissions)
set_found_permissions = set(found_permissions)


if len(set_included_permissions.difference(set_found_permissions)) == 0:
    print("ROLE PERMISSIONS PASSED")
else:
    print("ROLE PERMISSIONS FAILED")
