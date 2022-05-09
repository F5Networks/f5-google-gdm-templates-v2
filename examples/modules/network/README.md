
# Deploying Network Template

[![Releases](https://img.shields.io/github/release/F5Networks/f5-google-gdm-templates-v2.svg)](https://github.com/F5Networks/f5-google-gdm-templates-v2/releases)
[![Issues](https://img.shields.io/github/issues/F5Networks/f5-google-gdm-templates-v2.svg)](https://github.com/F5Networks/f5-google-gdm-templates-v2/issues)

## Contents

- [Deploying Network Template](#deploying-network-template)
  - [Contents](#contents)
  - [Introduction](#introduction)
  - [Prerequisites](#prerequisites)
  - [Important Configuration Notes](#important-configuration-notes)
    - [Template Input Parameters](#template-input-parameters)
    - [Template Outputs](#template-outputs)
  - [Resource Creation Flow Chart](#resource-creation-flow-chart)

## Introduction

This Google Deployment Manager template creates a virtual network, subnets, and route tables required to support F5 solutions. Link this template to create networks, subnets, and route tables required for F5 deployments.

## Prerequisites

 - None
 
## Important Configuration Notes

 - A sample template, `sample_network.yaml`, is included in this project. Use this example to see how to add network.py as a template into your templated solution.


### Template Input Parameters

**Required** means user input is required because there is no default value or an empty string is not allowed. If no value is provided, the template will fail to launch. In some cases, the default value may only work on the first deployment due to creating a resource in a global namespace and customization is recommended. See the Description for more details.

| Parameter | Required | Default | Type | Description |
| --- | --- | --- | --- | --- |
| autoCreateSubnets | No | false | boolean | When "true", newly created network is assigned the default CIDR of 10.128.0.0/9 and one subnet per region is created automatically. |
| name | Yes |  | string | Name used to create virtual network. |
| provisionPublicIp  | No | true | boolean |  When false, NAT gateway routers are created to support internet access on subnets. |
| uniqueString | No |  | string | Unique String used when creating object names or Tags. |
| subnets | No |  | array | Array of subnets along with their properties for each listed network. |
| subnets.properties. | No | | string | The proceeding parameters are used when defining subnets and autoCreateSubnets is not set to true. |
| subnets.properties.description | No |  | string | An optional description of this resource. |
| subnets.properties.enableFlowLogs | No |  | boolean | Whether to enable flow logging for this subnetwork. This field isn't supported with the purpose field set to `INTERNAL_HTTPS_LOAD_BALANCER`. |
| subnets.properties.ipCidrRange | Yes |  | string | The range of internal addresses that are owned by this subnetwork. Provide this property when you create the subnetwork. For example, `10.0.0.0/8` or `100.64.0.0/10`. Ranges must be unique and non-overlapping within a network. Only IPv4 is supported. The range can be any range listed in the Valid ranges list: https://cloud.google.com/vpc/docs/vpc#valid-ranges. |
| subnets.properties.name | Yes |  | string | Name used to create subnet. |
| subnets.properties.privateIpGoogleAccess | No |  | boolean | Whether the VMs in this subnet can access Google services without assigned external IP addresses. |
| subnets.properties.privateIpv6GoogleAccess | No |  | string | The private IPv6 google access type for the VMs in this subnet. | 
| subnets.properties.region | Yes | | string | Region where the Subnetwork resides. |
| subnets.properties.secondaryIpRanges[] | No |  | array | An array of configurations for secondary IP ranges for VM instances contained in this subnetwork. The primary IP of such VM must belong to the primary ipCidrRange of the subnetwork. The alias IPs may belong to either primary or secondary ranges. |
| subnets.properties.secondaryIpRanges[].ipCidrRange | No |  | string | The range of IP addresses belonging to this subnetwork secondary range. Ranges must be unique and non-overlapping with all primary and secondary IP ranges within a network. Only IPv4 is supported. The range can be any range listed in the Valid ranges list: https://cloud.google.com/vpc/docs/vpc#valid-ranges. |
| subnets.properties.secondaryIpRanges[].rangeName | No |  | string | The name associated with this subnetwork secondary range, used when adding an alias IP range to a VM instance. The name must be 1-63 characters long and comply with RFC1035. The name must be unique within the subnetwork. |


### Template Outputs

| Name | Required Resource | Type | Description |
| --- | --- | --- | --- |
| name | Network | string | Network resource name. |
| provisionPublicIp | No | boolean | When false, NAT gateway routers created to support internet access on subnets. |
| selflink | Network | string | URI (SelfLink) for network resource. |
| subnets | Subnets | array | Array with subnets information. |
| subnets.properties.cidrRange | Subnet | string | Range of internal addresses owned by the subnet. |
| subnets.properties.gatewayAddress | Subnet | string | Gateway address for subnet. |
| subnets.properties.network | Subnet | string | URL for network where subnet belongs. |
| subnets.properties.region | Subnet | string | Region where the subnet resides. |
| subnets.properties.selflink | Subnet | string | URI (SelfLink) for subnet resource. |


## Resource Creation Flow Chart

![Resource Creation Flow Chart](https://github.com/F5Networks/f5-google-gdm-templates-v2/blob/main/examples/images/google-network-module.png)
