
# Deploying Network Template

[![Releases](https://img.shields.io/github/release/f5networks/f5-google-gdm-templates-v2.svg)](https://github.com/f5networks/f5-google-gdm-templates-v2/releases)
[![Issues](https://img.shields.io/github/issues/f5networks/f5-google-gdm-templates-v2.svg)](https://github.com/f5networks/f5-google-gdm-templates-v2/issues)

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

 - A sample template, 'sample_network.yaml', has been included in this project. Use this example to see how to add network.py as a template into your templated solution.


### Template Input Parameters

| Parameter | Required | Description |
| --- | --- | --- |
| autoCreateSubnets | No | When "true",  newly created network is assigned the default CIDR of 10.128.0.0/9 and one subnet per region is created automatically |
| name | Yes | Name used to create virtual network. |
| subnets | No | Array of subnets along with their properties for each listed network. |
| type | Yes | A value of network.py is used for this template. |
| uniqueString | No | Unique String used when creating object names or Tags. |
| **subnets.properties.** | No | The proceeding parameters are used when defining subnets and autoCreateSubnets is not set to true. |
| subnets.properties.description | No | An optional description of this resource. |
| subnets.properties.enableFlowLogs | No | Whether to enable flow logging for this subnetwork. This field isn't supported with the purpose field set to INTERNAL_HTTPS_LOAD_BALANCER |
| subnets.properties.ipCidrRange | Yes | The range of internal addresses that are owned by this subnetwork. Provide this property when you create the subnetwork. For example, 10.0.0.0/8 or 100.64.0.0/10. Ranges must be unique and non-overlapping within a network. Only IPv4 is supported. The range can be any range listed in the Valid ranges list: https://cloud.google.com/vpc/docs/vpc#valid-ranges. |
| subnets.properties.name | Yes | Name used to create subnet. |
| subnets.properties.privateIpGoogleAccess | No | Whether the VMs in this subnet can access Google services without assigned external IP addresses. |
| subnets.properties.privateIpv6GoogleAccess | No | The private IPv6 google access type for the VMs in this subnet. | 
| subnets.properties.region | Yes | Region where the Subnetwork resides. |
| subnets.properties.secondaryIpRanges[] | No | An array of configurations for secondary IP ranges for VM instances contained in this subnetwork. The primary IP of such VM must belong to the primary ipCidrRange of the subnetwork. The alias IPs may belong to either primary or secondary ranges. |
| subnets.properties.secondaryIpRanges[].ipCidrRange | No | The range of IP addresses belonging to this subnetwork secondary range. Ranges must be unique and non-overlapping with all primary and secondary IP ranges within a network. Only IPv4 is supported. The range can be any range listed in the Valid ranges list: https://cloud.google.com/vpc/docs/vpc#valid-ranges. |
| subnets.properties.secondaryIpRanges[].rangeName | No | The name associated with this subnetwork secondary range, used when adding an alias IP range to a VM instance. The name must be 1-63 characters long, and comply with RFC1035. The name must be unique within the subnetwork. |

### Template Outputs

| Name | Description | Required Resource | Type |
| --- | --- | --- | --- |
| name | Network resource name. | Network | string
| provisionPublicIp | When false, nat gateway routers created to support internet access on subnets. | No | boolean |
| selflink | URI (SelfLink) for network resource. | Network | string |
| subnets | Array with subnets information. | Subnets | array |
| subnets.properties.cidrRange | Range of internal addresses owned by the subnet. | Subnet | string |
| subnets.properties.gatewayAddress | Gateway address for for subnet. | Subnet | string |
| subnets.properties.network | URL for network were subnet belongs. | Subnet | string |
| subnets.properties.region | Region where the subnet resides. | Subnet | string |
| subnets.properties.selflink | URI (SelfLink) for subnet resource. | Subnet | string |


## Resource Creation Flow Chart

![Resource Creation Flow Chart](https://github.com/F5Networks/f5-google-gdm-templates-v2/blob/master/examples/images/google-network-module.png)
