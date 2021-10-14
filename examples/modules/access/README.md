# Deploying Access Template

[![Releases](https://img.shields.io/github/release/F5Networks/f5-google-gdm-templates-v2.svg)](https://github.com/F5Networks/f5-google-gdm-templates-v2/releases)
[![Issues](https://img.shields.io/github/issues/F5Networks/f5-google-gdm-templates-v2.svg)](https://github.com/F5Networks/f5-google-gdm-templates-v2/issues)

## Contents

- [Deploying Access Template](#deploying-access-template)
  - [Contents](#contents)
  - [Introduction](#introduction)
  - [Prerequisites](#prerequisites)
  - [Important Configuration Notes](#important-configuration-notes)
    - [Template Input Parameters](#template-input-parameters)
    - [Template Outputs](#template-outputs)
  - [Resource Creation Flow Chart](#resource-creation-flow-chart)

## Introduction

This Google Deployment Manager template creates an IAM Service Account to be used by the BIG-IP and other modules to manage permissions for access to Google Cloud services such as storage and compute.

## Prerequisites

 - None

## Important Configuration Notes

 - A sample template, `sample_access.yaml`, is included in this project. Use this example to see how to add access.py as a template into your templated solution.

### Template Input Parameters

| Parameter | Required | Description |
| --- | --- | --- |
| solutionType | Yes | Type of solution you want to deploy. Options include: standard, secret, storageBucket, secretStorage, failover, custom |
| uniqueString | Yes | Unique String used when creating object names or Tags. For example: `my-deployment` |
| includedPermissions | Yes | A space-delimited list of permissions to assign to the custom role. Required when solutionType is 'custom'. See example below for more information. |

#### Example template when using custom solutionType
The following example will create a role with custom permissions.

```yaml
---
# Copyright 2021 F5 Networks All rights reserved.
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

| Name | Description | Required Resource | Type |
| --- | --- | --- | --- |
| service_account_email | Service Account Email ID. | Access | string |
| custom_role_name | Name of custom role. | Access | string |
| custom_role_permissions | Permissions granted to custom role. | Access | string |

## Resource Creation Flow Chart

![Resource Creation Flow Chart](https://github.com/F5Networks/f5-google-gdm-templates-v2/blob/main/examples/images/google-access-module.png)