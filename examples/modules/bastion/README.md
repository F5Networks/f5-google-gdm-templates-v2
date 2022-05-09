# Deploying Bastion Template

[![Releases](https://img.shields.io/github/release/F5Networks/f5-google-gdm-templates-v2.svg)](https://github.com/F5Networks/f5-google-gdm-templates-v2/releases)
[![Issues](https://img.shields.io/github/issues/F5Networks/f5-google-gdm-templates-v2.svg)](https://github.com/F5Networks/f5-google-gdm-templates-v2/issues)

## Contents

- [Deploying Bastion Template](#deploying-bastion-template)
  - [Contents](#contents)
  - [Introduction](#introduction)
  - [Prerequisites](#prerequisites)
  - [Important Configuration Notes](#important-configuration-notes)
    - [Template Input Parameters](#template-input-parameters)
    - [Template Outputs](#template-outputs)
  - [Resource Creation Flow Chart](#resource-creation-flow-chart)

## Introduction

This Google Deployment Manager template creates a bastion host used for accessing BIG-IP within private network which is required to support F5 solutions.

## Prerequisites

 - None

## Important Configuration Notes

 - A sample template, `sample_bastion.yaml`, is included in this project. Use this example to see how to add bastion.py as a template into your templated solution.

### Template Input Parameters

**Required** means user input is required because there is no default value or an empty string is not allowed. If no value is provided, the template will fail to launch. In some cases, the default value may only work on the first deployment due to creating a resource in a global namespace and customization is recommended. See the Description for more details.

| Parameter | Required | Default | Type | Description |
| --- | --- | --- | --- | --- |
| application | No | f5app | string | Application label. |
| autoscalers | No |  | array | Required when provisioning autoscale group. List of declaration of settings used for provisioning autoscalers. More information around REST APIs is on [Google Cloud Documentation](https://cloud.google.com/compute/docs/reference/rest/v1/autoscalers). |
| cost | No | f5cost | string | Cost Center label. |
| environment | No | f5env | string | Environment label. |
| group | No | f5group | string | Group label. |
| instanceGroupManagers | No |  | array | Required when provisioning autoscale group. List of declaration of settings used for provisioning instanceGroupManagers. More information around REST APIs is on [Google Cloud Documentation](https://cloud.google.com/compute/docs/reference/rest/v1/instanceGroupManagers). |
| instances | No |  | f5group | Required when provisioning a single instance. List of declaration of settings used for provisioning instances. More information around REST APIs is on [Google Cloud Documentation](https://cloud.google.com/compute/docs/reference/rest/v1/instances). |
| instanceTemplates | No |  | array | Required when provisioning autoscale group. List of declaration of settings used for provisioning instanceTemplates. More information around REST APIs is on [Google Cloud Documentation](https://cloud.google.com/compute/docs/reference/rest/v1/instanceTemplates). |
| instanceTemplateVersion | No | 1 | integer | Version of the instance template to create. When updating deployment properties of the application instances, you must provide a unique value for this parameter. |
| instanceType | Yes | n1-standard-1 | string | App instance type. For example: `n1-standard-1` |
| osImage | No | 'projects/ubuntu-os-cloud/global/images/family/ubuntu-1804-lts' | string | Self link for OS Image.  |
| owner | No | f5owner | string | Owner label. |
| uniqueString | Yes |  | string | Unique String used when creating object names or Tags. For example: `my-deployment` |
| zone | Yes |  | string | Name of the availability zone where the application will be placed. |

### Template Outputs

| Name | Required Resource | Type | Description |
| --- | --- | --- | --- |
| bastionName | Bastion | string | Bastion resource name. |
| bastionIp | Bastion | string | Network IP for Bastion resource. |
| bastionInstanceGroupName | Bastion | string | Instance group resource name. |

## Resource Creation Flow Chart

![Resource Creation Flow Chart](https://github.com/F5Networks/f5-google-gdm-templates-v2/blob/main/examples/images/google-bastion-module.png)
