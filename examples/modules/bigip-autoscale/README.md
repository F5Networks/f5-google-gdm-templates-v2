# Deploying BIG-IP Autoscale Template

[![Releases](https://img.shields.io/github/release/F5Networks/f5-google-gdm-templates-v2.svg)](https://github.com/F5Networks/f5-google-gdm-templates-v2/releases)
[![Issues](https://img.shields.io/github/issues/F5Networks/f5-google-gdm-templates-v2.svg)](https://github.com/F5Networks/f5-google-gdm-templates-v2/issues)

## Contents

- [Deploying BIG-IP Autoscale Template](#deploying-bigip-autoscale-template)
  - [Contents](#contents)
  - [Introduction](#introduction)
  - [Prerequisites](#prerequisites)
  - [Important Configuration Notes](#important-configuration-notes)
    - [Template Input Parameters](#template-input-parameters)
    - [Template Outputs](#template-outputs)

## Introduction

This Google Deployment Manager template creates an autoscale group of BIG-IP instances; each instance is initialized and onboarded according to the provided declaration. 

## Prerequisites

 - F5-bigip-runtime-init configuration file required. See https://github.com/F5Networks/f5-bigip-runtime-init for more details on F5-bigip-runtime-init SDK. See example runtime-init-conf.yaml in the repository.
 - Declarative Onboarding (DO) declaration: See example autoscale_do_payg.json or autoscale_do_bigiq.json in the repository.
 - AS3 declaration: See example autoscale_a3.json in the repository.
 - Telemetry Streaming (TS) declaration if using custom metrics. See example autoscale_ts.json in the repository.


## Important Configuration Notes

- A sample template, `sample_bigip_autoscale.yaml`, is included in this project. Use this example to see how to add bigip.json as a linked template into your templated solution.
- Troubleshooting: The log location for f5-bigip-runtime-init onboarding is ``/var/log/cloud/bigIpRuntimeInit.log``. By default, the log level is set to info; however, you can set a custom log level by exporting the F5_BIGIP_RUNTIME_INIT_LOG_LEVEL environment variable before invoking f5-bigip-runtime-init in commandToExecute: 
```export F5_BIGIP_RUNTIME_INIT_LOG_LEVEL=silly && bash ', variables('runtimeConfigPackage'), ' azure 2>&1```


### Template Input Parameters

**Required** means user input is required because there is no default value or an empty string is not allowed. If no value is provided, the template will fail to launch. In some cases, the default value may only work on the first deployment due to creating a resource in a global namespace and customization is recommended. See the Description for more details.

| Parameter | Required | Default | Type |  Description |
| --- | --- | --- | --- | --- |
| application | No | f5app | string |Application label. |
| autoscalers | Yes |  | array | List of declaration of settings used for provisioning autoscalers. More information around REST APIs is on [Google Cloud Documentation](https://cloud.google.com/compute/docs/reference/rest/v1/autoscalers). |
| bigIpRuntimeInitPackageUrl | Yes |  | string | URL for BIG-IP Runtime Init package. | 
| bigIpRuntimeInitConfig | Yes |  | string | Supply a URL to the bigip-runtime-init configuration file in YAML or JSON format, or an escaped JSON string to use for f5-bigip-runtime-init configuration. |
| cost | No | f5cost | string | Cost Center label. |
| environment | No | f5env | string | Environment label. | 
| group | No | f5group | string | Group label. |
| healthChecks | Yes |  | array | List of declaration of settings used for provisioning HealthChecks which defines health checks used by other cloud resources. More information around REST APIs is on [Google Cloud Documentation](https://cloud.google.com/compute/docs/reference/rest/v1/healthChecks). |
| instanceGroupManagers | Yes |  | string | Required when provisioning autoscale group. List of declaration of settings used for provisioning instanceGroupManagers. More information around REST APIs is on [Google Cloud Documentation](https://cloud.google.com/compute/docs/reference/rest/v1/instanceGroupManagers). |
| instanceTemplateVersion | No | 1 |  | Version of the instance template to create. When updating deployment properties of the BIG-IP instances, you must provide a unique value for this parameter. |
| instanceType | Yes |  | string | Instance type assigned to the application. For example: `n1-standard-1`. | 
| instanceTemplates | Yes |  | array | Required when provisioning autoscale group. List of declaration of settings used for provisioning instanceTemplates. More information around REST APIs is on [Google Cloud Documentation](https://cloud.google.com/compute/docs/reference/rest/v1/instanceTemplates). |
| networkSelfLink | Yes |  | string | Self Link of the network to use to deploy the application.  | 
| owner | No | f5owner | string | Owner label. |
| provisionPublicIp | No | true | boolean | Select true if you would like to provision a public IP address for accessing the BIG-IP instance(s). |
| serviceAccountEmail | Yes |  | string | Enter the Google service account to use for autoscale API calls. For example: `username@projectname.iam.serviceaccount.com`. |
| subnetSelfLink | Yes |  | string | Self Link of the subnetwork to use to deploy the application. | 
| targetPools | Yes |  | array | List of settings for provisioning target pools. More information around REST APIs is on [Google Cloud Documentation](https://cloud.google.com/compute/docs/reference/rest/v1/targetPools). |
| uniqueString | Yes |  | string | Unique String used when creating object names or Tags.|


### Template Outputs

| Name | Required Resource | Type | Description |
| --- | --- | --- | --- |
| bigipAutoscaleName |  All resources |  string | BIG-IP Autoscale resource name. |
| instanceGroup | Instance Group | string | Self-link to BIG-IP Instance group. |
| targetPool | Target Pool | string | Self-link to Target Pool |
