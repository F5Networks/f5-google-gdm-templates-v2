# Deploying Access Template

[![Releases](https://img.shields.io/github/release/F5Networks/f5-google-gdm-templates-v2.svg)](https://github.com/F5Networks/f5-google-gdm-templates-v2/releases)
[![Issues](https://img.shields.io/github/issues/F5Networks/f5-google-gdm-templates-v2.svg)](https://github.com/F5Networks/f5-google-gdm-templates-v2/issues)

## Contents

- [Deploying Access Template](#deploying-access-template)
    - [Contents](#contents)
    - [Introduction](#introduction)
    - [Prerequisites](#prerequisites)
    - [Important Configuration Notes](#important-configuration-notes)
    - [Resources Provisioning](#resources-provisioning)
        - [IAM Permissions by Solution Type](#iam-permissions-by-solution-type)
        - [Template Input Parameters](#template-input-parameters)
            - [Example template when using custom solutionType](#example-template-when-using-custom-solutiontype)
        - [Template Outputs](#template-outputs)
    - [Resource Creation Flow Chart](#resource-creation-flow-chart)

## Introduction

This solution uses a Google Deployment Manager template to launch a stack for provisioning Access related items. This template can be deployed as a standalone; however, the main intention is to use as a module for provisioning Access related resources:

  - Service accounts
  - Custom IAM roles 
  - Service account bindings

This solution creates IAM roles based on the following **solutionTypes**:

  - standard
    - Service Discovery *(used by AS3)*
    - Google Cloud metrics and logging *(used by Telemetry Streaming)*
  - secret
    - Permissions from standard +
    - Access a secret from Google secrets manager *(used by Runtime-Init)*
  - storage
    - Permissions from standard + 
    - Google storage bucket *(used by Telemetry Streaming for remote logging or Cloud Failover Extension for State File Storage)*
  - remoteLogging
    - Permissions from standard + 
    - Access a secret from Google secrets manager *(used by Runtime-Init)*
    - Google storage bucket *(used by Telemetry Streaming for remote logging or Cloud Failover Extension for State File Storage)*
  - failover
    - Permissions from standard + 
    - Access a secret from Google secrets manager *(used by Runtime-Init)*
    - Google storage bucket *(used by Telemetry Streaming for remote logging or Cloud Failover Extension for State File Storage)*
    - Update permissions for IP addresses/routes *(used by Cloud Failover Extension)*

## Prerequisites

 - This template creates service accounts, custom IAM roles, and service account bindings. The Google APIs Service Agent service account must be granted the Role Administrator and Project IAM Admin roles before deployment can succeed. For more information about this account, see the [Google-managed service account documentation](https://cloud.google.com/iam/docs/maintain-custom-roles-deployment-manager)

## Important Configuration Notes

 - A sample template, `sample_access.yaml`, is included in this project. Use this example to see how to add access.py as a template into your templated solution.

 ## Resources Provisioning

  * [Service Account](https://cloud.google.com/iam/docs/service-accounts)
    - This account can be passed to the BIG-IP module template to provide access to required APIs/services from the BIG-IP instance(s).
  * [IAM Role](https://cloud.google.com/iam/docs/understanding-roles)
  * [Service Account Binding](https://cloud.google.com/sdk/gcloud/reference/iam/service-accounts/add-iam-policy-binding)
    - Links the previously created Service Account and IAM Role.

 ### IAM Permissions by Solution Type

These are the IAM permissions produced by each type of solution supported by this template. For more details about the purpose of each permission, see the [CFE documentation for Google Cloud](https://clouddocs.f5.com/products/extensions/f5-cloud-failover/latest/userguide/gcp.html#create-and-assign-an-iam-role).

| Permission | Solution Type |
| --- | --- |
| compute.forwardingRules.get | standard, secret, failover | 
| compute.forwardingRules.list | standard, secret, failover | 
| compute.forwardingRules.setTarget | failover | 
| compute.globalOperations.get | standard, secret, storage, remoteLogging, failover | 
| compute.instances.get | standard, secret, failover |
| compute.instances.list | standard, secret, failover | 
| compute.instances.updateNetworkInterface | failover | 
| compute.networks.updatePolicy | failover | 
| compute.routes.create | failover | 
| compute.routes.delete | failover | 
| compute.routes.get | failover | 
| compute.routes.list | failover | 
| compute.targetInstances.get | standard, secret, failover | 
| compute.targetInstances.list | standard, secret, failover | 
| compute.targetInstances.use | failover | 
| logging.logEntries.create | standard, secret, remoteLogging, failover | 
| monitoring.metricDescriptors.create | standard, secret, remoteLogging | 
| monitoring.metricDescriptors.get | standard, secret, remoteLogging | 
| monitoring.metricDescriptors.list | standard, secret, remoteLogging | 
| monitoring.monitoredResourceDescriptors.get | standard, secret, remoteLogging | 
| monitoring.monitoredResourceDescriptors.list | standard, secret, remoteLogging |
| monitoring.timeSeries.create | standard, secret, remoteLogging | 
| resourcemanager.projects.get | secret, remoteLogging, failover | 
| secretmanager.versions.access | secret, failover |
| secretmanager.versions.get | secret, failover | 
| secretmanager.versions.list | secret, failover | 
| storage.buckets.get | storage, remoteLogging, failover | 
| storage.buckets.list | storage, remoteLogging, failover | 
| storage.buckets.update | storage, remoteLogging, failover | 
| storage.objects.create | storage, remoteLogging, failover |
| storage.objects.delete | storage, remoteLogging, failover | 
| storage.objects.get | storage, remoteLogging, failover | 
| storage.objects.list | storage, remoteLogging, failover | 
| storage.objects.update | storage, remoteLogging, failover | 

### Template Input Parameters

**Required** means user input is required because there is no default value or an empty string is not allowed. If no value is provided, the template will fail to launch. In some cases, the default value may only work on the first deployment due to creating a resource in a global namespace and customization is recommended. See the Description for more details.

| Parameter | Required | Default | Type | Description |
| --- | --- | --- | --- | --- |
| solutionType | Yes | 'standard' | string | Type of solution you want to deploy. Options include: standard, secret, storageBucket, secretStorage, failover, and custom. |
| uniqueString | Yes |  | string | Unique String used when creating object names or Tags. For example: `my-deployment` |
| includedPermissions | Yes |  | string | A space-delimited list of permissions to assign to the custom role. Required when solutionType is 'custom'. See the example below for more information. |

#### Example template when using custom solutionType
The following example will create a role with custom permissions.

```yaml
---
# Copyright 2022 F5 Networks All rights reserved.
#
# Version 0.1.0s

imports:
  - path: access.py
resources:
  - name: access
    type: access.py
    properties:
      solutionType: custom
      uniqueString: myApp
      includedPermissions:
        - compute.instances.create
          compute.instances.get
          compute.instances.list
```

### Template Outputs

| Name | Required Resource | Type | Description |
| --- | --- | --- | --- |
| service_account_email | Access | string | Service Account Email ID. |
| custom_role_name | Access | string |  Name of custom role. |
| custom_role_permissions | Access | string | Permissions granted to custom role. |

## Resource Creation Flow Chart

![Resource Creation Flow Chart](https://github.com/F5Networks/f5-google-gdm-templates-v2/blob/main/examples/images/google-access-module.png)