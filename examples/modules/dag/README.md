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
| firewalls | No | list of declaration of settings used for provisioning Firewalls rules intended to deny or allow ingress traffic to and egress traffic from your instances. More information around REST APIs is on Google Cloud Documentation https://cloud.google.com/compute/docs/reference/rest/v1/firewalls |
| forwardingRules | No | list of declaration of settings used for provisioning ForwardingRule which represents the fortend configuration of GCP load balancer. More information around REST APIs is on Google Cloud Documentation https://cloud.google.com/compute/docs/reference/rest/v1/forwardingRules |
| backendServices | No | list of declaration of settings used for provisioning RegionBackendServices which defines how GCP load balancers distribute traffic. More information around REST APIs is on Google Cloud Documentation https://cloud.google.com/compute/docs/reference/rest/v1/regionBackendServices |
| healthChecks | No | list of declaration of settings used for provisioning HealthChecks which defines health checks used by other cloud resources. More information around REST APIs is on Google Cloud Documentation https://cloud.google.com/compute/docs/reference/rest/v1/healthChecks |
| uniqueString | Yes | Unique String used when creating object names or Tags. |

### Template Outputs

| Name | Description | Required Resource | Type |
| --- | --- | --- | --- |
| dagName | deployment name | None | String |
| backendService | Self link to Backend Service | Backend Service | URL |
