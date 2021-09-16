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

This Google Deployment Manager template creates a bastion host used for accessing BIGIP within private network which is required to support F5 solutions.

## Prerequisites

 - None

## Important Configuration Notes

 - A sample template, 'sample_bastion.yaml', has been included in this project. Use this example to see how to add bastion.py as a template into your templated solution.

### Template Input Parameters

| Parameter | Required | Description |
| --- | --- | --- |
| application | No | Application label. |
| autoscalers | No | Required when provisioning autoscale group. List of declaration of settings used for provisioning autoscalers. More information around REST APIs is on Google Cloud Documentation https://cloud.google.com/compute/docs/reference/rest/v1/autoscalers |
| cost | No | Cost Center label. |
| environment | No | Environment label. |
| group | No | Group label. |
| instanceGroupManagers | No | Required when provisioning autoscale group. List of declaration of settings used for provisioning instanceGroupManagers. More information around REST APIs is on Google Cloud Documentation https://cloud.google.com/compute/docs/reference/rest/v1/instanceGroupManagers |
| instances | No | Required when provisioning a single instance. List of declaration of settings used for provisioning instances. More information around REST APIs is on Google Cloud Documentation https://cloud.google.com/compute/docs/reference/rest/v1/instances |
| instanceTemplates | No | Required when provisioning autoscale group. List of declaration of settings used for provisioning instanceTemplates. More information around REST APIs is on Google Cloud Documentation https://cloud.google.com/compute/docs/reference/rest/v1/instanceTemplates |
| instanceTemplateVersion | No | Version of the instance template to create. When updating deployment properties of the application instances, you must provide a unique value for this parameter. |
| instanceType | Yes | App instance type. e.g. n1-standard-1 |
| osImage | No | Self link for OS Image  |
| owner | No | Owner label. |
| uniqueString | Yes | Unique String used when creating object names or Tags. e.g. my-deployment |
| zone | Yes | Name of the availability zone where the application will be placed. |

### Template Outputs

| Name | Description | Required Resource | Type |
| --- | --- | --- | --- |
| bastionName | Bastion resource name. | Bastion | string |
| bastionIp | Network IP for Bastion resource. | Bastion | string |
| bastionInstanceGroupName | Instance group resource name. | Bastion | string |

## Resource Creation Flow Chart

![Resource Creation Flow Chart](https://github.com/F5Networks/f5-google-gdm-templates-v2/blob/main/examples/images/google-bastion-module.png)
