# Deploying Function Template

[![Releases](https://img.shields.io/github/release/F5Networks/f5-google-gdm-templates-v2.svg)](https://github.com/F5Networks/f5-google-gdm-templates-v2/releases)
[![Issues](https://img.shields.io/github/issues/F5Networks/f5-google-gdm-templates-v2.svg)](https://github.com/F5Networks/f5-google-gdm-templates-v2/issues)

## Contents

- [Deploying Function Template](#deploying-function-template)
  - [Contents](#contents)
  - [Introduction](#introduction)
  - [Prerequisites](#prerequisites)
  - [Important Configuration Notes](#important-configuration-notes)
    - [Template Input Parameters](#template-input-parameters)
    - [Template Outputs](#template-outputs)
    
## Introduction

This Google Deployment Manager template creates cloud resources intended for provisioning and triggering cloud/serverless function used for revoking BIGIP licenses from BIGIQ side.

## Prerequisites

 - None

## Important Configuration Notes

 - A sample template, 'sample_function.yaml', has been included in this project. Use this example to see how to add function.py as a template into your templated solution.

### Template Input Parameters

**Required** means user input is required because there is no default value or an empty string is not allowed. If no value is provided, the template will fail to launch. In some cases, the default value may only work on the first deployment due to creating a resource in a global namespace and customization is recommended. See the Description for more details.

| Parameter | Required | Default | Type | Description |
| --- | --- | --- | --- | --- |
| functions | No |  | array | List of declaration of settings used for provisioning cloud functions. More information around REST APIs is on [Google Cloud Documentation](https://cloud.google.com/functions/docs/reference/rest/v1/projects.locations.functions).| 
| jobs | No |  | array | List of declaration of settings used for provisioning scheduled jobs. More information around REST APIs is on [Google Cloud Documentation](https://cloud.google.com/scheduler/docs/reference/rest/v1/projects.locations.jobs).  | 
| topics | No |  | array | List of declaration of settings used for provisioning PubSub topics. More information around REST APIs is on [Google Cloud Documentation](https://cloud.google.com/pubsub/docs/reference/rest/v1/projects.topics).  | 
| uniqueString | Yes |  | string | Unique String used when creating object names or Tags. |

### Template Outputs

| Name | Required Resource | Type | Description |
| --- | --- | --- | --- |
| deploymentName | None | string | Deployment name |
