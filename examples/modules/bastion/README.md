# Deploying Bastion Template

[![Releases](https://img.shields.io/github/release/f5networks/f5-google-gdm-templates-v2.svg)](https://github.com/f5networks/f5-google-gdm-templates-v2/releases)
[![Issues](https://img.shields.io/github/issues/f5networks/f5-google-gdm-templates-v2.svg)](https://github.com/f5networks/f5-google-gdm-templates-v2/issues)

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

This Google Deployment Manager template creates a bastion host *********TBD********** required to support F5 solutions.

## Prerequisites

 - None

## Important Configuration Notes

 - A sample template, 'sample_bastion.yaml', has been included in this project. Use this example to see how to add bastion.py as a template into your templated solution.

### Template Input Parameters

| Parameter | Required | Description |
| --- | --- | --- |
| application | No | Application label. |
| availabilityZone | Yes | Name of the availability zone where the bastion host will be placed. |
| createAutoscaleGroup | No | Choose true to create the bastion instances in an autoscaling configuration. |
| cost | No | Cost Center label. |
| environment | No | Environment label. | 
| group | No | Group label. |
| instanceTemplateVersion | No | Version of the instance template to create. When updating deployment properties of the bastion instances, you must provide a unique value for this parameter. |
| instanceType | Yes | App instance type. e.g. n1-standard-1 |
| uniqueString | Yes | Unique String used when creating object names or Tags. e.g. my-deployment |
| networkSelfLink | Yes | Self Link of the network to use to deploy the bastion. |
| osImage | No | Self link for OS Image  |
| owner | No | Owner label. |
| subnetSelfLink | Yes | Self Link of the subnetwork to use to deploy the bastion. |

### Template Outputs

| Name | Description | Required Resource | Type |
| --- | --- | --- | --- |
| bastionName | Bastion resource name. | Bastion | string |
| bastionIp | Network IP for Bastion resource. | Bastion | string |
| bastionInstanceGroupName | Instance group resource name. | Bastion | string |

## Resource Creation Flow Chart

![Resource Creation Flow Chart](https://github.com/F5Networks/f5-google-gdm-templates-v2/blob/master/examples/images/google-bastion-module.png)
