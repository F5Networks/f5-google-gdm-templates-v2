# Deploying BIG-IP Standalone Template

[![Releases](https://img.shields.io/github/release/F5Networks/f5-google-gdm-templates-v2.svg)](https://github.com/F5Networks/f5-google-gdm-templates-v2/releases)
[![Issues](https://img.shields.io/github/issues/F5Networks/f5-google-gdm-templates-v2.svg)](https://github.com/F5Networks/f5-google-gdm-templates-v2/issues)

## Contents

- [Deploying BIG-IP Standalone Template](#deploying-bigip-standalone-template)
  - [Contents](#contents)
  - [Introduction](#introduction)
  - [Prerequisites](#prerequisites)
  - [Important Configuration Notes](#important-configuration-notes)
    - [Template Input Parameters](#template-input-parameters)
    - [Template Outputs](#template-outputs)

## Introduction

This Google Deployment Manager template creates a single BIG-IP instance; each instance is initialized and onboarded according to provided declaration. 

## Prerequisites

 - F5-bigip-runtime-init configuration file required. See https://github.com/F5Networks/f5-bigip-runtime-init for more details on F5-bigip-runtime-init SDK. See example runtime-init-conf.yaml in the repository.
 - Declarative Onboarding (DO) declaration: See example standalone_do_payg.json or standalone_do_bigiq.json in the repository.
 - AS3 declaration: See example standalone_a3.json in the repository.
 - Telemetry Streaming (TS) declaration if using custom metrics. See example standalone_ts.json in the repository.


## Important Configuration Notes

- A sample template, `sample_bigip_standalone.yaml`, is included in this project. Use this example to see how to add bigip.json as a linked template into your templated solution.
- Troubleshooting: The log location for f5-bigip-runtime-init onboarding is ``/var/log/cloud/bigIpRuntimeInit.log``. By default, the log level is set to info; however, you can set a custom log level by exporting the F5_BIGIP_RUNTIME_INIT_LOG_LEVEL environment variable before invoking f5-bigip-runtime-init in commandToExecute: 
```export F5_BIGIP_RUNTIME_INIT_LOG_LEVEL=silly && bash ', variables('runtimeConfigPackage'), ' gcp 2>&1```


### Template Input Parameters

**Required** means user input is required because there is no default value or an empty string is not allowed. If no value is provided, the template will fail to launch. In some cases, the default value may only work on the first deployment due to creating a resource in a global namespace and customization is recommended. See the Description for more details.

| Parameter | Required | Default | Type | Description |
| --- | --- | --- | --- | --- |
| bigIpRuntimeInitPackageUrl | Yes |  | string | URL for BIG-IP Runtime Init package. | 
| bigIpRuntimeInitConfig | Yes |  | string | Supply a URL to the bigip-runtime-init configuration file in YAML or JSON format, or an escaped JSON string to use for f5-bigip-runtime-init configuration. |
| imageName | Yes |  | string | BIG-IP image name.|
| instanceType | Yes |  | string | Instance type assigned to the application. For example: `n1-standard-1`.|
| name | Yes |  | string | Name used for instance.| 
| networkInterfaces | Yes |  | array | Array of interface configurations for Instance. A minimum of one is required.|
| networkInterfaces.accessConfigs | No |  | string | Used to define ONE_TO_ONE_NATS (external public address) for interface.|
| networkInterfaces.aliasIpRanges | No |  | string | Used to define additional alias addresses to interface.|
| networkInterfaces.network | Yes |  | string | Defines network attached to interface.|
| networkInterfaces.networkIP | No |  | string | Defines static IP attached to interface.|
| networkInterfaces.subnetwork | Yes |  | string | Defines subnetwork attached to interface.|
| region | Yes |  | string | Enter the region where you want to deploy the application. For example: `us-west1`.|
| storageBuckets | Yes |  | string | Creates storage buckets.| 
| tags.items | No |  | array | An array of tags used to match traffic against network interfaces.|
| targetInstances | Yes |  | array | List of settings for provisioning target instances. More information around REST APIs is on [Google Cloud Documentation](https://cloud.google.com/compute/docs/reference/rest/v1/targetInstances). |
| uniqueString | Yes |  | string | Unique String used when creating object names or Tags.|
| zone | Yes |  | string | Enter the zone where you want to deploy the application. For example: `us-west1-a`.|


### Template Outputs

| Name | Required Resource | Type | Description |
| --- | --- | --- | --- |
| instanceName |  All resources |  string | BIG-IP instance resource name. |
| targetInstanceSelfLink |  All resources |  string | BIG-IP target instance self link. |
