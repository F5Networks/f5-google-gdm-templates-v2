# Example Templates

- [Example Templates](#example-templates)
  - [Introduction](#introduction)
  - [Template Types](#template-types)
    - [Solution Parent Templates](#solution-parent-templates)
    - [Modules](#modules)
  - [Usage](#usage)
  - [BIG-IP Configuration](#big-ip-configuration)
  - [Cloud Configuration](#cloud-configuration)
  - [Style Guide](#style-guide)
  - [Getting Help](#getting-help)
    - [Filing Issues](#filing-issues)

## Introduction

The examples here leverage the modular [nested templates](https://cloud.google.com/deployment-manager/docs/step-by-step-guide/using-multiple-templates) design to provide maximum flexibility when authoring solutions using F5 BIG-IP.

Example deployments use parent templates to deploy child templates (or modules) to facilitate quickly standing up entire stacks (complete with **example** network, application, and BIG-IP tiers). 

As a basic framework, an example full stack deployment may consist of: 

- **(Parent) Solution Template** (for example, Quickstart, Failover or Autoscale)
  -  **(Child) Network Template** - creates virtual networks (VPC), subnets, internet/NAT gateways, DHCP options, network ACLs, and other network related resources. 
  -  **(Child) Application Template** - creates a generic application for demonstrating live traffic through the BIG-IP.
  -  **(Child) DAG/Ingress Template** - creates resources required to get traffic to the BIG-IP (for example, Public IPs, External and Internal Load Balancers, Firewall Rules).
  -  **(Child) Access Template** - creates Identity and Access related resources, like IAM Roles and Service Accounts, with permissions for various use cases (for example, accessing a secret in a cloud vault, Storage, etc.)
  -  **(Child) Function Template** - creates functions used for tasks like managing licenses for an Autoscale Group of BIG-IP instances licensed with BIG-IQ, convenience functions, etc.
  -  **(Child) BIG-IP Template** *(existing-stack)* - creates a BIG-IP instance or instances in an GCP Instance Group, failover cluster, etc. 

Together, the Network and Application templates serve as a basic harness to illustrate various BIG-IP solutions. The DAG/Ingress, Access, and Function Templates provide various pre-requisites for the BIG-IP solution. 

***Disclaimer:*** F5 does not require or have any recommendations on leveraging linked stacks in production. They are used here simply to provide useful tested/validated full stack examples and illustrate various solutions' resource dependencies, configurations, etc, which you may want or need to customize, regardless of the deployment method used. 
 

## Template Types

Templates are grouped into the following categories:

### Solution Parent Templates

  - **Quickstart**: <br> This parent template deploys a standalone BIG-IP in a bare minimal full-stack example. To reduce pre-requisites/dependencies and complexity for first time users, this solution does not leverage IAM roles or cloud functions like solutions below, which generally require more advanced permissions. Standalone BIG-IP VEs are primarily used for Dev/Test/Staging, replacing/upgrading individual instances in traditional failover clusters, and/or manually scaling out. <br>

  - **Failover Cluster**: <br> These parent templates deploy more than one BIG-IP VE in a ScaleN cluster (a traditional High Availability Pair in most cases), as well as resources required by the solution, for a full stack example. Failover clusters are primarily used to replicate traditional Active/Standby BIG-IP deployments. In these deployments an individual BIG-IP VE in the cluster owns, or is Active for, a particular IP address. For example, the BIG-IP VEs will fail over services from one instance to another by remapping IP addresses, routes, etc, based on Active/Standby status. Failover is implemented either via API (API calls to the cloud platform vs network protocols like Gratuitous ARP, route updates, etc), or via an upstream service (like a native loud balancer), which will only send traffic to the active instance for that service based on a health monitor. In all cases, a single BIG-IP VE will be active for a single IP address.

  - **Autoscale**: <br> These parent templates deploy an Autoscale Group of BIG-IP VE instances, as well as resources required by the solution, for a full stack example. The BIG-IP VEs are "All Active" and are primarily used to scale an L7 service on a single wildcard virtual (although you can add additional services using ports).<br> Unlike previous solutions, this solution leverages the more traditional Autoscale configuration management pattern where each instance is created with an identical configuration as defined in the Autoscale Group's model (also known as GCP's "Instance Template"). Scale sizes are no longer restricted to the smaller limitations of the BIG-IP's cluster. The BIG-IP's configuration is now defined in a single convenient yaml-based [F5 BIG-IP Runtime Init](https://github.com/f5devcentral/f5-bigip-runtime-init) configuration file. For instance, if you need to change the configuration on the instances in the deployment, you update the the model by passing the new version of config file via the template's *bigIpRuntimeInitConfig* input parameter. The Autoscale's provider will update the instances to the new model according to its rolling update policy.

### Modules

  - These child templates create the GCP resources that compose a full stack deployment. They are referenced as linked deployment resources from the solution parent templates (Quickstart, Failover, Autoscale, etc).<br>
  The parent templates manage passing inputs to the child templates and using their outputs as inputs to other child templates.<br>

    #### Module Types:
      - **Network**: Use this template to create a reference network stack. This template creates virtual networks and subnets. 
      - **Application**: Use this template to deploy an example application. This template creates a generic application, based on the f5-demo-app container, for demonstrating live traffic through the BIG-IP. You can specify a different container or application to use when deploying the example template.
      - **Disaggregation/Ingress** (DAG): Use this template to create resources required to get or distribute traffic to the BIG-IP instance(s). For example: Public IP Addresses, internal/external Load Balancers, and accompanying resources.
      - **Access**: Use this template to create IAM Roles and Service Accounts for standalone, failover, or Autoscale solution. 
      - **Function**: Use this template to create functions used for tasks like managing licenses for an Autoscale Group of BIG-IP instances licensed with BIG-IQ, convenience functions, etc.
      - **BIG-IP**: Use these templates to create the BIG-IP Virtual Machine instance(s). For example, a standalone instance or an Autoscale Group. The BIG-IP modules can be used independently from the linked stack examples here (for example, in an "existing-stack"). The BIG-IP's configuration, now defined in a single convenient yaml-based [F5 BIG-IP Runtime Init](https://github.com/f5devcentral/f5-bigip-runtime-init) configuration file, leverages [F5 Automation Tool Chain](https://www.f5.com/pdf/products/automation-toolchain-overview.pdf) declarations, which are easier to author, validate, and maintain as code.
    

With modules, related resources that fall under different administrative domains are grouped together and can be reused without one-to-one resource mapping. For example, if the team deploying BIG-IP does not have permission to create IAM roles, they can point a security team to the ACCESS module section for an example of the minimal permissions needed. If customizing, users may choose to decompose or recompose even further into simpler single templates. For example, depending on what resource creation permissions users have, that same team may want to instead create a single dependencies module of resources they do have permissions for, found in various dependency modules like DAG and FUNCTION, and just reference the existing role the security team provided, security group the network provided, etc. Or if ALL the dependencies are pre-provided, a user can potentially even use the BIG-IP module by itself. See customizing section [below](#cloud-configuration).


## Usage

1. Clone or fork the repository
    ```
    git clone git@github.com:f5networks/f5-google-gdm-templates-v2.git

2. Navigate to the parent solution template directory:

    Examples: 
    * quickstart
    * autoscale/payg

    First see individual READMEs for pre-requisites.

3. Copy or Modify the example yaml configuration file and update the parameters. See the README for any REQUIRED parameters.

4. Deploy via the [Google CLI](https://cloud.google.com/sdk/docs/install). 
  
    ```bash
    gcloud deployment-manager deployments create ${DEPLOYMENT_NAME} --config ${CONFIG_FILE}`
    ```

    For example:
    ```bash
    gcloud deployment-manager deployments create myquickstart --config sample_quickstart.yaml
    ```

    NOTE:
    - *DEPLOYMENT_NAME*<br>This name must be unique.<br>
    - *CONFIG_FILE*<br>If your file is not in the same directory as where running the command, include the full file path in the command.


## BIG-IP Configuration

These solutions also aim to enable much more flexibility with customizing BIG-IP configurations through the use of [F5 BIG-IP Runtime Init](https://GitHub.com/f5networks/f5-bigip-runtime-init) and [F5 Automation Tool Chain](https://www.f5.com/pdf/products/automation-toolchain-overview.pdf) declarations which are easier to author, validate and maintain as code.

You will most likely want or need to change the BIG-IP configuration. This involves customizing a [F5 BIG-IP Runtime Init](https://github.com/f5networks/f5-bigip-runtime-init) configuration file and passing it through the `bigIpRuntimeInitConfig` template parameter as a URL. See [F5 BIG-IP Runtime Init](https://github.com/f5networks/f5-bigip-runtime-init) for more details on how to customize the configuration. 
 
Example Runtime Init config files are provided in the solution's `/bigip-configurations` directory. In some cases (for example, PAYG licensed solutions), you can often start with default example config URL from this public GitHub repo directly. However, in most cases (for example, any BYOL or BIG-IQ licensed solutions), this requires customizing the config file and publishing to a location accessible from the BIG-IP at deploy time (typically: a version control system, local/private file server/service, etc). See individual solution README for details.

## Cloud Configuration 

In addition to changing the BIG-IP Configuration, you may often want to customize the cloud resources, which involves editing the templates themselves.

A high-level overview of customizing the templates may look like:

1. Clone or fork the repository.
    ```
    git clone git@github.com:f5networks/f5-google-gdm-templates-v2.git
    ```
    *Optional*: Create a custom branch.
    
    git checkout -b \<branch\>
    ```
    git checkout -b customizations
    ```

2. Edit the templates themselves.

    Commit changes
    ```
    git add <FILES_MODIFIED>
    git commit -m "customizations added"
    ```

3. Deploy via the [Google CLI](https://cloud.google.com/sdk/docs/install). 
  
```bash
gcloud deployment-manager deployments create ${DEPLOYMENT_NAME} --config ${CONFIG_FILE}
```

4. Optionally, re-publish the repository or BIG-IP configurations to a location reachable by the BIG-IPs. See [BIG-IP Configuration](#big-ip-configuration) above.


## Style Guide

Variables that are meant to be customized by users are often encased in `<>`, are prefixed or contain `YOUR`, and are CAPITALIZED to stand out. Replace anything in `<>` with **YOUR_VALUE**. For example:
  - In config files, replace:
      ```yaml
      secretId: <YOUR_SECRET_ID>
      ```
    with
      ```yaml
      secretId: mybigIpAdminPassword
      ```
  - In CLI examples, replace:
      ```shell 
      create auth user <YOUR_WEBUI_USERNAME> password ...
      ```
    with
      ```shell
      create auth user myCustomUser password ...
      ```

For convenience, for some examples that are often run in bash (for example, gcloud) have values that should be replaced in bash variable format. Replace anything in `${}` with **YOUR_VALUE**. For example,
  - Replace: 
      ```bash
      gcloud deployment-manager deployments create ${DEPLOYMENT_NAME} --config ${CONFIG_FILE}
      ```
    with 
      ```bash 
      gcloud deployment-manager deployments create myquickstart --config sample_quickstart.yaml
      ```
  - Or leverage the convenience and set as bash variables before running command:
      ```bash
      DEPLOYMENT="myquickstart"
      CONFIG_FILE="sample_quickstart.yaml"
      gcloud deployment-manager deployments create ${DEPLOYMENT_NAME} --config ${CONFIG_FILE}
      ```


## Getting Help

Due to the heavy customization requirements of external cloud resources and BIG-IP configurations in these solutions, F5 does not provide technical support for deploying, customizing, or troubleshooting the templates themselves. However, the various underlying products and components used (for example: [F5 BIG-IP Virtual Edition](https://clouddocs.f5.com/cloud/public/v1/), [F5 BIG-IP Runtime Init](https://github.com/F5Networks/f5-bigip-runtime-init), [F5 Automation Toolchain](https://www.f5.com/pdf/products/automation-toolchain-overview.pdf) extensions, and [Cloud Failover Extension (CFE)](https://clouddocs.f5.com/products/extensions/f5-cloud-failover/latest/)) in the solutions located here are F5-Supported and capable of being deployed with other orchestration tools. Read more about [Support Policies](https://www.f5.com/company/policies/support-policies). Problems found with the templates deployed as-is should be reported via a GitHub issue.


For help with authoring and support for custom CST2 templates, we recommend engaging F5 Professional Services (PS).


### Filing Issues

If you find an issue, we would love to hear about it.

- Use the **[Issues](https://github.com/F5Networks/f5-google-gdm-templates-v2/issues)** link on the GitHub menu bar in this repository for items such as enhancement, feature requests and bug fixes. Tell us as much as you can about what you found and how you found it.
