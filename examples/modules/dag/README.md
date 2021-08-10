# Deploying Dag/Ingress Template

[![Releases](https://img.shields.io/github/release/f5networks/f5-google-gdm-templates-v2.svg)](https://github.com/f5networks/f5-google-gdm-templates-v2/releases)
[![Issues](https://img.shields.io/github/issues/f5networks/f5-google-gdm-templates-v2.svg)](https://github.com/f5networks/f5-google-gdm-templates-v2/issues)

## Contents

- [Deploying Dag/Ingress Template](#deploying-dagingress-template)
  - [Contents](#contents)
  - [Introduction](#introduction)
  - [Prerequisites](#prerequisites)
  - [Important Configuration Notes](#important-configuration-notes)
    - [Template Input Parameters](#template-input-parameters)
    - [Template Outputs](#template-outputs)


## Introduction

This Google Deployment Manager template creates various cloud resources to get traffic to BIG-IP solutions

## Prerequisites

 - None

## Important Configuration Notes

 - A sample template, 'sample_dag.yaml', has been included in this project. Use this example to see how to add dag.py as a template into your templated solution.

### Template Input Parameters

| Parameter | Required | Description |
| --- | --- | --- |
| application | No | Application label. |
| applicationVipPort | No | List application port(s) for external application access separated by a space. |
| applicationPort | No | List application port(s) for internal google load balancer separated by a space. A maximum of 5 ports can be specified. This is only required when using internal loadbalancer (numberOfForwardingRules equals 1). |
| cost | No | Cost Center label. |
| environment | No | Environment label. | 
| group | No | Group label. |
| guiPortMgmt | No |  Enter the BIG-IP Management Port, the default is '443'. |
| instanceGroups | No | A list of instance group self links for the service. |
| instances | Yes | A list of instances self links for the service. |
| networkSelfLinkApp | No | Self Link of the application network. |
| subnetSelfLinkApp| No | Self Link to the application subnet. | 
| networkSelfLinkExternal | Yes | Self Link of the external network.| 
| subnetSelfLinkExternal | Yes | Self Link to the external subnet. |
| networkSelfLinkInternal | No | Self Link of the internal network. |
| subnetSelfLinkInternal | No | Self Link to the internal subnet. | 
| networkSelfLinkMgmt | Yes | Self Link of the mgmt network. | 
| subnetSelfLinkMgmt | Yes | Self Link to the mgmt subnet. |
| numberOfNics | Yes | Enter the number of network interfaces created on each BIG-IP VE instance. When 1 is specified, the management and external firewall rules are combined on the management network. |
| numberOfIntForwardingRules | No | Specify the number of forwarding rules to create for internal application traffic, for example, '0' or '1'. |
| numberOfForwardingRules | No | Enter the number of forwarding rules to create, for example '1'.  All integers from 1 to the max quota for the forwarding rules resource type are allowed. |
| owner | No | Owner label. |
| restrictedSrcAddressMgmt | No | This field restricts management access to specific networks or addresses. Enter an IP address or address range in CIDR notation separated by a space. |
| restrictedSrcAddressApp | No | This field restricts web application access to a specific network or address; the port is defined using applicationPort parameter. Enter an IP address or address range in CIDR notation separated by a space. | 
| restrictedSrcAddressInternalApp | No | This field restricts web application access to a specific private network or address. Enter an IP address or address range in CIDR notation separated by a space. This is only required when using an internal load balancer (numberOfForwardingRules equals 1).
| uniqueString | Yes | Unique String used when creating object names or Tags.

### Template Outputs

| Name | Description | Required Resource | Type |
| --- | --- | --- | --- |
| dagName | deployment name | None | String |
| region | region name | None | String |
| backendService | Self link to Backend Service | Backend Service | URL |
| targetPool | Self link to Target Pool | Target Pool | URL | 
| appTrafficAddressN | ip address used for application forwarding rule | Forwarding Rule | String |
| internalTrafficAddressN | ip address used for internal forwarding rule | Internal Forwarding Rule | String |
