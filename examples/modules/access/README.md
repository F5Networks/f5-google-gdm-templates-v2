# Deploying Access Template

[![Releases](https://img.shields.io/github/release/f5networks/f5-google-gdm-templates-v2.svg)](https://github.com/f5networks/f5-google-gdm-templates-v2/releases)
[![Issues](https://img.shields.io/github/issues/f5networks/f5-google-gdm-templates-v2.svg)](https://github.com/f5networks/f5-google-gdm-templates-v2/issues)

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

 - A sample template, 'sample_access.yaml', has been included in this project. Use this example to see how to add access.py as a template into your templated solution.

### Template Input Parameters

| Parameter | Required | Description |
| --- | --- | --- |
| solutionType | Yes | Type of solution you want to deploy - standard, secret, storageBucket, secretStorage, failover |
| storageName | Yes | Storage Bucket for remote logging, failover solution etc. |
| secretId | Yes | ID of the secret stored in Secret Manager |
| uniqueString | Yes | Unique String used when creating object names or Tags. e.g. my-deployment |

### Template Outputs

| Name | Description | Required Resource | Type |
| --- | --- | --- | --- |
| service_account_email | Service Account Email ID. | Access | string |
| custom_role_name | Name of custom role. | Access | string |
| custom_role_permissions | Permissions granted to custom role. | Access | string |

## Resource Creation Flow Chart

![Resource Creation Flow Chart](https://github.com/F5Networks/f5-google-gdm-templates-v2/blob/master/examples/images/google-access-module.png)