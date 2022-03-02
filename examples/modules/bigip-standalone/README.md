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

| Parameter | Required | Description |
| --- | --- | --- |
| bigIpRuntimeInitPackageUrl | Yes | URL for BIG-IP Runtime Init package. | 
| bigIpRuntimeInitConfig | Yes | Supply a URL to the bigip-runtime-init configuration file in YAML or JSON format, or an escaped JSON string to use for f5-bigip-runtime-init configuration. |
| bigIpPeerAddr | No | Type the static self IP address of the remote host here. Leave empty if not configuring peering with a remote host on this device. IP address parameter must be in the form x.x.x.x. |
| imageName | Yes | BIG-IP image name.|
| instanceType | Yes | Instance type assigned to the application. For example: `n1-standard-1`.|
| name | Yes | Name used for instance.| 
| networkInterfaces | Yes | Array of interface configurations for Instance. A minimum of one is required.|
| networkInterfaces.accessConfigs | No | Used to define ONE_TO_ONE_NATS (external public address) for interface.|
| networkInterfaces.aliasIpRanges | No | Used to define additional alias addresses to interface.|
| networkInterfaces.network | Yes | Defines network attached to interface.|
| networkInterfaces.networkIP | No | Defines static IP attached to interface.|
| networkInterfaces.subnetwork | Yes | Defines subnetwork attached to interface.|
| region | Yes | Enter the region where you want to deploy the application. For example: `us-west1`.|
| tags.items | No | An array of tags used to match traffic against network interfaces.|
| targetInstances | Yes | List of settings for provisioning target instances. More information around REST APIs is on [Google Cloud Documentation](https://cloud.google.com/compute/docs/reference/rest/v1/targetInstances). |
| uniqueString | Yes | Unique String used when creating object names or Tags.|
| zone | Yes | Enter the zone where you want to deploy the application. For example: `us-west1-a`.|


### Template Outputs

| Name | Description | Required Resource | Type |
| --- | --- | --- | --- |
| instanceName | BIG-IP instance resource name |  All resources |  String |
| targetInstanceSelfLink | BIG-IP target instance self link |  All resources |  String |
