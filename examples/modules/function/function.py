# Copyright 2021 F5 Networks All rights reserved.
#
# Version 0.1.0

# pylint: disable=W,C,R,duplicate-code,line-too-long

"""Creates the access"""
CLOUDSCHEDULER_URL_BASE = 'https://cloudscheduler.googleapis.com'
PUBSUB_URL_BASE = 'https://pubsub.googleapis.com'
CLOUDFUNCTION_URL_BASE = 'https://cloudfunctions.googleapis.com'

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



def create_schedule_job(context, deployment_context):
    """Create schedule job."""
    required_properties = [
        'name'
    ]
    optional_properties = [
        'description',
        'schedule',
        'timeZone',
        'retryConfig',
        'pubsubTarget',
        'appEngineHttpTarget',
        'httpTarget'
    ]

    properties = {
        'parent':  f"projects/{ deployment_context.env['project'] }/locations/{ deployment_context.properties.get('region', 'us-west1') }"
    }

    properties.update(populate_properties(context, required_properties, optional_properties))

    schedule_job = {
        'name': context.get('name'),
        'type': 'gcp-types/cloudscheduler-v1:projects.locations.jobs',
        'properties': properties
    }
    return schedule_job


def create_topic(context):
    """Create pubsub job."""
    required_properties = [
        'name',
        'topic'
    ]
    optional_properties = [
        'labels',
        'messageStoragePolicy',
        'kmsKeyName',
        'schemaSettings'
        'messageRetentionDuration'
    ]
    properties = populate_properties(context, required_properties, optional_properties)

    pubSubTopic = {
        'name': context.get('name'),
        'type': 'gcp-types/pubsub-v1:projects.topics',
        'properties': properties
    }
    return pubSubTopic


def create_cloud_function(context, deployment_context):
    """Create pubsub job."""
    required_properties = [
        'name'
    ]
    optional_properties = [
        'description',
        'entryPoint',
        'runtime',
        'timeout',
        'availableMemoryMb',
        'serviceAccountEmail',
        'labels',
        'environmentVariables',
        'buildEnvironmentVariables',
        'network',
        'maxInstances',
        'vpcConnector',
        'vpcConnectorEgressSettings',
        'ingressSettings',
        'buildWorkerPool',
        'sourceToken',
        'sourceArchiveUrl',
        'sourceRepository',
        'sourceUploadUrl',
        'httpsTrigger',
        'eventTrigger'
    ]

    properties = {
        'parent': f"projects/{ deployment_context.env['project'] }/locations/{ deployment_context.properties.get('region', 'us-west2') }",
        'function': context.get('name')
    }

    properties.update(populate_properties(context, required_properties, optional_properties))

    cloudFunction = {
        'name': context.get('name'),
        'type': 'gcp-types/cloudfunctions-v1:projects.locations.functions',
        'properties': properties
    }
    return cloudFunction


def generate_name(prefix, suffix):
    """Generate unique name."""
    return prefix + "-" + suffix


def generate_config(context):
    """Entry point for the deployment resources."""
    name = context.properties.get('name') or \
           context.env['name']
    deployment_name = generate_name(context.properties['uniqueString'], name)

    resources = []
    outputs = [
        {
            'name': 'deploymentName',
            'value': deployment_name
        }
    ]

    for job in context.properties.get('jobs', []):
        resources.append(create_schedule_job(job, context))

    for topic in context.properties.get('topics', []):
        resources.append(create_topic(topic))

    for function in context.properties.get('functions', []):
        resources.append(create_cloud_function(function, context))

    return {'resources': resources, 'outputs': outputs}
