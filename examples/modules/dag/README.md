# Deploying Dag/Ingress Template

[![Releases](https://img.shields.io/github/release/F5Networks/f5-google-gdm-templates-v2.svg)](https://github.com/F5Networks/f5-google-gdm-templates-v2/releases)
[![Issues](https://img.shields.io/github/issues/F5Networks/f5-google-gdm-templates-v2.svg)](https://github.com/F5Networks/f5-google-gdm-templates-v2/issues)

## Contents

- [Deploying Dag/Ingress Template](#deploying-dagingress-template)
  - [Contents](#contents)
  - [Introduction](#introduction)
  - [Prerequisites](#prerequisites)
  - [Important Configuration Notes](#important-configuration-notes)
    - [Template Input Parameters](#template-input-parameters)
    - [Template Outputs](#template-outputs)


## Introduction

This Google Deployment Manager template creates various cloud resources to get traffic to BIG-IP solutions.

## Prerequisites

 - None

## Important Configuration Notes

 - A sample template, `sample_dag.yaml`, is included in this project. Use this example to see how to add dag.py as a template into your templated solution.

### Template Input Parameters

**Required** means user input is required because there is no default value or an empty string is not allowed. If no value is provided, the template will fail to launch. In some cases, the default value may only work on the first deployment due to creating a resource in a global namespace and customization is recommended. See the Description for more details.

| Parameter | Required | Default | Type | Description |
| --- | --- | --- | --- | --- |
| firewalls | No |  | array | List of declaration of settings used for provisioning Firewalls rules intended to deny or allow ingress traffic to and egress traffic from your instances. More information around REST APIs is on [Google Cloud Documentation](https://cloud.google.com/compute/docs/reference/rest/v1/firewalls). |
| forwardingRules | No |  | array | List of declaration of settings used for provisioning ForwardingRule, which represents the frontend configuration of GCP load balancers. More information around REST APIs is on [Google Cloud Documentation](https://cloud.google.com/compute/docs/reference/rest/v1/forwardingRules). |
| backendServices | No |  | array | List of declaration of settings used for provisioning RegionBackendServices, which defines how GCP load balancers distribute traffic. More information around REST APIs is on [Google Cloud Documentation](https://cloud.google.com/compute/docs/reference/rest/v1/regionBackendServices). |
| healthChecks | No |  | array | List of declaration of settings used for provisioning HealthChecks, which defines health checks used by other cloud resources. More information around REST APIs is on [Google Cloud Documentation](https://cloud.google.com/compute/docs/reference/rest/v1/healthChecks). |
| uniqueString | Yes |  | string | Unique String used when creating object names or Tags. |

### Template Outputs

| Name | Required Resource | Type | Description |
| --- | --- | --- | --- |
| dagName | None | String | Deployment name. |
| backendService | Backend Service | URL | Self link to Backend Service. |