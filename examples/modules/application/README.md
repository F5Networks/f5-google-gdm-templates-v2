# Deploying Application Template

[![Releases](https://img.shields.io/github/release/F5Networks/f5-google-gdm-templates-v2.svg)](https://github.com/F5Networks/f5-google-gdm-templates-v2/releases)
[![Issues](https://img.shields.io/github/issues/F5Networks/f5-google-gdm-templates-v2.svg)](https://github.com/F5Networks/f5-google-gdm-templates-v2/issues)

## Contents

- [Deploying Application Template](#deploying-application-template)
  - [Contents](#contents)
  - [Introduction](#introduction)
  - [Prerequisites](#prerequisites)
  - [Important Configuration Notes](#important-configuration-notes)
    - [Template Input Parameters](#template-input-parameters)
    - [Template Outputs](#template-outputs)
  - [Resource Creation Flow Chart](#resource-creation-flow-chart)

## Introduction

This Google Deployment Manager template creates a client application using an existing network and firewall required to support F5 solutions.

## Prerequisites

 - None

## Important Configuration Notes

 - A sample template, `sample_application.yaml`, is included in this project. Use this example to see how to add application.py as a template into your templated solution.

### Template Input Parameters

**Required** means user input is required because there is no default value or an empty string is not allowed. If no value is provided, the template will fail to launch. In some cases, the default value may only work on the first deployment due to creating a resource in a global namespace and customization is recommended. See the Description for more details.

| Parameter | Required | Default | Type |  Description |
| --- | --- | --- | --- | --- |
| appContainerName | No | 'f5devcentral/f5-demo-app:latest' | string | Name of the docker container to deploy in the application VM. |
| application | No | f5app | string | Application label. |
| autoscalers | No |  | array | Required when provisioning autoscale group. List of declaration of settings used for provisioning autoscalers. More information around REST APIs is on [Google Cloud Documentation](https://cloud.google.com/compute/docs/reference/rest/v1/autoscalers). |
| cost | No | f5cost | string | Cost Center label. |
| environment | No | f5env | string | Environment label. |
| group | No | f5group | string | Group label. |
| instanceGroupManagers | No |  | string | Required when provisioning autoscale group. List of declaration of settings used for provisioning instanceGroupManagers. More information around REST APIs is on [Google Cloud Documentation](https://cloud.google.com/compute/docs/reference/rest/v1/instanceGroupManagers). |
| instances | No |  | array | Required when provisioning a single instance. List of declaration of settings used for provisioning instances. More information around REST APIs is on [Google Cloud Documentation](https://cloud.google.com/compute/docs/reference/rest/v1/instances). |
| instanceTemplates | No |  | array | Required when provisioning autoscale group. List of declaration of settings used for provisioning instanceTemplates. More information around REST APIs is on [Google Cloud Documentation](https://cloud.google.com/compute/docs/reference/rest/v1/instanceTemplates). |
| instanceTemplateVersion | No | 1 | integer | Version of the instance template to create. When updating deployment properties of the application instances, you must provide a unique value for this parameter. |
| instanceType | Yes | n1-standard-1 | string | App instance type. For example: `n1-standard-1` |
| owner | No | f5owner | string | Owner label. |
| uniqueString | Yes |  | string | Unique String used when creating object names or Tags. For example: `my-deployment` |
| zone | Yes |  | string | Name of the availability zone where the application will be placed. |

### Template Outputs

| Name | Required Resource | Type | Description |
| --- | --- | --- | --- |
| applicationIp | Application | string | Network IP for Application resource. |
| applicationName | Application | string | Application resource name. |
| instanceGroupName | Application | string | Instance group resource name. |

## Resource Creation Flow Chart

![Resource Creation Flow Chart](https://github.com/F5Networks/f5-google-gdm-templates-v2/blob/main/examples/images/google-application-module.png)
