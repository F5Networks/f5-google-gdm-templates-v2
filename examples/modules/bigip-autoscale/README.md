# Deploying BIGIP Autoscale Template

[![Releases](https://img.shields.io/github/release/f5networks/f5-google-gdm-templates-v2.svg)](https://github.com/f5networks/f5-google-gdm-templates-v2/releases)
[![Issues](https://img.shields.io/github/issues/f5networks/f5-google-gdm-templates-v2.svg)](https://github.com/f5networks/f5-google-gdm-templates-v2/issues)

## Contents

- [Deploying BIGIP Autoscale Template](#deploying-bigip-autoscale-template)
  - [Contents](#contents)
  - [Introduction](#introduction)
  - [Prerequisites](#prerequisites)
  - [Important Configuration Notes](#important-configuration-notes)
    - [Template Input Parameters](#template-input-parameters)
    - [Template Outputs](#template-outputs)

## Introduction

This Google Deployment Manager template creates an autoscale group of BIGIP instnaces; each instance is initialized and onboarded according to provided declaration. 

## Prerequisites

 - F5-bigip-runtime-init configuration file required. See https://github.com/F5Networks/f5-bigip-runtime-init for more details on F5-bigip-runtime-init SDK. See example runtime-init-conf.yaml in the repository.
 - Declarative Onboaring (DO) declaration: See example autoscale_do_payg.json or autoscale_do_bigiq.json in the repository.
 - AS3 declaration: See example autoscale_a3.json in the repository.
 - Telemetry Streaming (TS) declaration if using custom metrics. See example autoscale_ts.json in the repository.


## Important Configuration Notes

- A sample template, 'sample_bigip_autoscale.yaml', has been included in this project. Use this example to see how to add bigip.json as a linked template into your templated solution.
- Troubleshooting: The log location for f5-bigip-runtime-init onboarding is ``/var/log/cloud/bigIpRuntimeInit.log``. By default, the log level is set to info; however, you can set a custom log level by exporting the F5_BIGIP_RUNTIME_INIT_LOG_LEVEL environment variable before invoking f5-bigip-runtime-init in commandToExecute: 
```export F5_BIGIP_RUNTIME_INIT_LOG_LEVEL=silly && bash ', variables('runtimeConfigPackage'), ' azure 2>&1```


### Template Input Parameters

| Parameter | Required | Description |
| --- | --- | --- |
| availabilityZone | Yes | Enter the availability zone where you want to deploy the application, for example 'us-west1-a'. |
| applicationVipPort | No | Application Port number |
| bigIpRuntimeInitPackageUrl | Yes | URL for BIG-IP Runtime Init package | 
| bigIpRuntimeInitConfig | Yes | Supply a URL to the bigip-runtime-init configuration file in YAML or JSON format, or an escaped JSON string to use for f5-bigip-runtime-init configuration. |
| coolDownPeriodSec | No | The application initialization period; the autoscaler uses the cool down period for scaling decisions. |
| instanceType | Yes | Instance type assigned to the application, for example 'n1-standard-1'. | 
| networkSelfLink | Yes | Self Link of the network to use to deploy the application.  | 
| maxNumReplicas | No | Maximum number of replicas that autoscaler can provision  |
| minNumReplicas | No | Minimum number of replicas that autoscaler can provision |
| serviceAccountEmail | Yes | Enter the Google service account to use for autoscale API calls, for example 'username@projectname.iam.serviceaccount.com'. |
| subnetSelfLink | Yes | Self Link of the subnetwork to use to deploy the application. | 
| targetGroupSelfLink | No | Target Pool self-link used for external loadbalancing |
| utilizationTarget | No | The target value of the metric that autoscaler should maintain. This must be a positive value. A utilization metric scales number of virtual machines handling requests to increase or decrease proportionally to the metric. |
| uniqueString | Yes | Unique String used when creating object names or Tags.|


### Template Outputs

| Name | Description | Required Resource | Type |
| --- | --- | --- | --- |
| bigipAutoscaleName | BIGIP Autoscale resource name |  All resources |  String |
| instanceGroup | Self-link to BIGIP Instance group | Instance Group | String |
| targetPool | Self-link to Target Pool | Target Pool | String |
