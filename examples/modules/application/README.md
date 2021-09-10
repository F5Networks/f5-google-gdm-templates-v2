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

 - A sample template, 'sample_application.yaml', has been included in this project. Use this example to see how to add application.py as a template into your templated solution.

### Template Input Parameters

| Parameter | Required | Description |
| --- | --- | --- |
| appContainerName | No | Name of the docker container to deploy in the application VM. |
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
| owner | No | Owner label. |
| uniqueString | Yes | Unique String used when creating object names or Tags. e.g. my-deployment |
| zone | Yes | Name of the availability zone where the application will be placed. |

### Template Outputs

| Name | Description | Required Resource | Type |
| --- | --- | --- | --- |
| applicationIp | Network IP for Application resource. | Application | string |
| applicationName | Application resource name. | Application | string |
| instanceGroupName | Instance group resource name. | Application | string |

## Resource Creation Flow Chart

![Resource Creation Flow Chart](https://github.com/F5Networks/f5-google-gdm-templates-v2/blob/main/examples/images/google-application-module.png)
