# Deploying the BIG-IP VE in Google - Example Failover BIG-IP HA Cluster - Virtual Machines

[![Releases](https://img.shields.io/github/release/F5Networks/f5-google-gdm-templates-v2.svg)](https://github.com/F5Networks/f5-google-gdm-templates-v2/releases)
[![Issues](https://img.shields.io/github/issues/F5Networks/f5-google-gdm-templates-v2.svg)](https://github.com/F5Networks/f5-google-gdm-templates-v2/issues)

## Contents

- [Deploying the BIG-IP VE in Google - Example Failover BIG-IP HA Cluster - Virtual Machines](#deploying-the-big-ip-ve-in-google---example-failover-big-ip-ha-cluster---virtual-machines)
  - [Contents](#contents)
  - [Introduction](#introduction)
  - [Diagram](#diagram)
  - [Prerequisites](#prerequisites)
  - [Important Configuration Notes](#important-configuration-notes)
    - [Template Input Parameters](#template-input-parameters)
    - [Template Outputs](#template-outputs)
    - [Existing Network Template Input Parameters](#existing-network-template-input-parameters)
    - [Existing Network Template Outputs](#existing-network-template-outputs)
  - [Deploying this Solution](#deploying-this-solution)
    - [Deploying via the Google CLI](#deploying-via-the-gcloud-cli)
    - [Changing the BIG-IP Deployment](#changing-the-big-ip-deployment)
  - [Validation](#validation)
    - [Validating the Deployment](#validating-the-deployment)
    - [Accessing the BIG-IP](#accessing-the-big-ip)
      - [WebUI](#webui)
      - [SSH](#ssh)
    - [Further Exploring](#further-exploring)
      - [WebUI](#webui-1)
      - [SSH](#ssh-1)
    - [Testing the WAF Service](#testing-the-waf-service)
    - [Testing Failover](#testing-failover)
  - [Deleting this Solution](#deleting-this-solution)
    - [Deleting the deployment via Google Console](#deleting-the-deployment-via-google-cloud-console)
    - [Deleting the deployment using the Google CLI](#deleting-the-deployment-using-the-gcloud-cli)
  - [Troubleshooting Steps](#troubleshooting-steps)
  - [Security](#security)
  - [BIG-IP Versions](#big-ip-versions)
  - [Supported Instance Types and Hypervisors](#supported-instance-types-and-hypervisors)
  - [Documentation](#documentation)
  - [Getting Help](#getting-help)
    - [Filing Issues](#filing-issues)

## Introduction

The goal of this solution is to reduce prerequisites and complexity to a minimum so with a few steps, a user can quickly deploy a BIG-IP, login and begin exploring the BIG-IP platform in a working full-stack deployment capable of passing traffic.

This solution uses a parent template to launch several linked child templates (modules) to create an example BIG-IP Highly Available (HA) solution using the F5 Cloud Failover Extension (CFE).  For information about this deployment, see the F5 Cloud Failover Extension [documentation](https://clouddocs.f5.com/products/extensions/f5-cloud-failover/latest/userguide/gcp.html). The linked templates are located in the [`examples/modules`](https://github.com/F5Networks/f5-google-gdm-templates-v2/tree/main/examples/modules) directory in this repository. *F5 recommends cloning this repository and modifying these templates to fit your use case.*

***Full Stack (failover.py)***<br>
Use the *failover.py* parent template to deploy an example full stack HA solution, complete with virtual network, bastion *(optional)*, dag/ingress, access, BIG-IP(s) and example web application.  

***Existing Network Stack (failover-existing-network.py)***<br>
Use the *failover-existing-network.py* parent template to deploy HA solution into an existing network infrastructure. This template expects the virtual network, subnets, and bastion host(s) have already been deployed. A example web application is also not part of this parent template as it intended use is for an existing environment.

The modules below create the following cloud resources:

- **Network**: This template creates Google networks and subnets. *(Full stack only)*
- **Bastion**: This template creates a bastion host for accessing the BIG-IP instances when no public IP address is used for the management interfaces. *(Full stack only)*
- **Application**: This template creates a generic example application for use when demonstrating live traffic through the BIG-IP instance. *(Full stack only)*
- **Disaggregation** _(DAG/Ingress)_: This template creates resources required to get traffic to the BIG-IP, including firewall rules.
- **Access**: This template creates a custom IAM role for the BIG-IP instances and other resources to gain access to Google Cloud services such as compute and storage.
- **BIG-IP**: This template creates a BIG-IP VM instance provisioned with Local Traffic Manager (LTM) and Application Security Manager (ASM).

By default, this solution creates a 3 VPC Networks, an example Web Application instance and two BIG-IP instances with three network interfaces each (one for management and two for dataplane/application traffic - called external and internal). Application traffic from the Internet traverses an external network interface configured with both public and private IP addresses. Traffic to the application traverses an internal network interface configured with a private IP address.

**_DISCLAIMER/WARNING_**: To reduce prerequisites and complexity to a bare minimum for evaluation purposes only, this template optionally provides immediate access to the management interface via a Public IP. At the very _minimum_, configure the **restrictedSrcAddressMgmt** parameter to limit access to your client IP or trusted network. In production deployments, management access should never be directly exposed to the Internet and instead should be accessed via typical management best practices like bastion hosts/jump boxes, VPNs, etc.

## Diagram

![Configuration Example](diagram.png)

For information about this type of deployment, see the F5 Cloud Failover Extension [documentation](https://clouddocs.f5.com/products/extensions/f5-cloud-failover/latest/userguide/gcp.html).

## Prerequisites

- This solution requires a **secret** stored in Google Cloud [Secrets Manager](
https://cloud.google.com/secret-manager/docs/creating-and-accessing-secrets)
 containing the password used to cluster and access the failover Pair. For example, to create a secret using the GCLOUD CLI: 
  ```bash
  # Use an editor of your choice to create file called password.txt. Ensure there is no newline at the end of the file.
  $ gcloud secrets create mySecretId --data-file="password.txt"
  ```
  - *NOTE:*
    - By default, the secret name used is `mySecretId`. To change this, see [Changing the BIG-IP Deployment](#changing-the-big-ip-deployment) for more details.
- This solution requires an [SSH key](https://cloud.google.com/compute/docs/instances/adding-removing-ssh-keys) uploaded the project for access to the BIG-IP instances.
- You must have installed the [Google Cloud SDK](https://cloud.google.com/sdk/downloads).
- This solution requires a Google Cloud account that can provision objects described in the solution using the gcloud CLI:
  ```bash
  gcloud deployment-manager deployments create ${DEPLOYMENT_NAME} --config ${CONFIG_FILE}
  ```
- This solution creates service accounts, custom IAM roles, and service account bindings. The Google APIs Service Agent service account must be granted the Role Administrator and Project IAM Admin roles before deployment can succeed. For more information about this account, see the Google-managed service account [documentation](https://cloud.google.com/iam/docs/maintain-custom-roles-deployment-manager)
- This solution requires you to accept any Google Cloud Marketplace "License/Terms and Conditions" for the images used in this solution.
  - By default, this solution uses [F5 BIG-IP Virtual Edition - BEST (PAYG - 25Mbps)](https://console.cloud.google.com/marketplace/product/f5-7626-networks-public/f5-big-ip-adc-hourly-best-25mbps)

## Important Configuration Notes

- By default, this solution modifies the username **admin** with a password set to value of the Google Secrets Manager secret which is provided in the BIGIP_PASSWORD parameter of the BIG-IP Runtime Init runtime_parameters configuration.

- This solution requires Internet access for:
  - Downloading additional F5 software components used for onboarding and configuring the BIG-IP (via github.com). Internet access is required via the management interface and then via a dataplane interface (for example, external Self-IP) once a default route is configured. See [Overview of Mgmt Routing](https://support.f5.com/csp/article/K13284) for more details. By default, as a convenience, this solution provisions Public IPs to enable this but in a production environment, outbound access should be provided by a `routed` SNAT service (for example: Cloud NAT, custom firewall, etc.). _NOTE: access via web proxy is not currently supported. Other options include 1) hosting the file locally and modifying the runtime-init package url and configuration files to point to local URLs instead or 2) baking them into a custom image, using the [F5 Image Generation Tool](https://clouddocs.f5.com/cloud/public/v1/ve-image-gen_index.html)._
  - Contacting native cloud services for various cloud integrations:
    - _Onboarding_:
      - [F5 BIG-IP Runtime Init](https://github.com/F5Networks/f5-bigip-runtime-init) - to fetch secrets from native vault services
    - _Operation_:
      - [F5 Application Services 3](https://clouddocs.f5.com/products/extensions/f5-appsvcs-extension/latest/) - for features like Service Discovery
      - [F5 Telemetry Streaming](https://clouddocs.f5.com/products/extensions/f5-telemetry-streaming/latest/) - for logging and reporting
      - [Cloud Failover Extension (CFE)](https://clouddocs.f5.com/products/extensions/f5-cloud-failover/latest/) - for updating IP and route mappings
    - Additional cloud services like private endpoints can be used to address calls to native services traversing the Internet.
    - See [Security](#security) section for more details.

- This solution template provides an **initial** deployment only for an "infrastructure" use case (meaning that it does not support managing the entire deployment exclusively via the template's "Redeploy" function). This solution leverages metadata to send the instance **startup script**, which is only used to provide an initial BIG-IP configuration and not as the primary configuration API for a long-running platform. Although "Redeploy" can be used to update some cloud resources, as the BIG-IP configuration needs to align with the cloud resources, like IPs to NICs, updating one without the other can result in inconsistent states, while updating other resources, like the **image** or **instanceType**, can trigger an entire instance re-deployment. For example, to upgrade software versions, traditional in-place upgrades should be leveraged. See [AskF5 Knowledge Base](https://support.f5.com/csp/article/K84554955) and [Changing the BIG-IP Deployment](#changing-the-big-ip-deployment) for more information.

- If you have cloned this repository to modify the templates or BIG-IP config files and published to your own location, you can use the **imports** section of the configuration template file to specify the new location of the customized templates and the **bigIpRuntimeInitConfig** input parameter to specify the new location of the BIG-IP Runtime-Init config. See main [/examples/README.md](#cloud-configuration) for more template customization details. See [Changing the BIG-IP Deployment](#changing-the-big-ip-deployment) for more BIG-IP customization details.

- In this solution, the BIG-IP VE has the [LTM](https://f5.com/products/big-ip/local-traffic-manager-ltm) and [ASM](https://f5.com/products/big-ip/application-security-manager-asm) modules enabled to provide advanced traffic management and web application security functionality.

- If you would like to view all available images, run the following command from the **gcloud** command line: `$ gcloud compute images list --project f5-7626-networks-public --filter="name~f5"`

- This directory contains a schema file which helps manage the required fields and set defaults to optional fields. For example, if you omit the property for bigIpRuntimeInitPackageUrl in your configuration file, we set the default URL to the latest available version.

- **Important**: For multi-NIC deployments, this solution configures the second interface of the instance as the MGMT interface. This allows the first interface to be used by Google Cloud resources such as forwarding rules and load balancers for application traffic. To connect to the MGMT interface (nic1) get the IP address from the instance properties and use your management tool of choice. Note: The Google Cloud console and gcloud SSH connection options target nic0 and will not connect to the instance correctly.

- This template can send non-identifiable statistical information to F5 Networks to help us improve our templates. You can disable this functionality by setting the **autoPhonehome** system class property value to false in the F5 Declarative Onboarding declaration. See [Sending statistical information to F5](#sending-statistical-information-to-f5).

- See [trouble shooting steps](#troubleshooting-steps) for more details.

### Template Input Parameters
**Required** means user input is required because there is no default value or an empty string is not allowed. If no value is provided, the template will fail to launch. In some cases, the default value may only work on the first deployment due to creating a resource in a global namespace and customization is recommended. See the Description for more details.
Note: These are specified in the configuration file. See sample_quickstart.yaml

| Parameter | Required | Default | Type |  Description |
| --- | --- | --- | --- | --- |
| appContainerName | No | 'f5devcentral/f5-demo-app:latest' | string | The name of a container to download and install which is used for the example application server(s). If this value is left blank, the application module template is not deployed. |
| application | No | f5app | string | Application Tag. |
| bigIpImageName | No | f5-bigip-16-1-2-2-0-0-28-payg-best-25mbps-220505074742 | string | Name of BIG-IP custom image found in the Google Cloud Marketplace. Example value: `f5-bigip-16-1-2-2-0-0-28-payg-best-25mbps-220505074742`. You can find the names of F5 marketplace images in the README for this template or by running the command: `gcloud compute images list --project f5-7626-networks-public --filter="name~f5"`. |
| bigIpInstanceType | No | n1-standard-4 | string | Instance type assigned to the application, for example 'n1-standard-4'. |
| bigIpExternalSelfIp01 | No | 10.0.1.11 | string | External Private IP Address for BIGIP Instance A. IP address parameter must be in the form x.x.x.x. |
| bigIpExternalSelfIp02 | No | 10.0.1.12 | string | External Private IP Address for BIGIP Instance B. IP address parameter must be in the form x.x.x.x. |
| bigIpInternalSelfIp01 | No | 10.0.2.11 | string | Internal Private IP Address for BIGIP Instance A. IP address parameter must be in the form x.x.x.x. |
| bigIpInternalSelfIp02 | No | 10.0.2.12 | string | Internal Private IP Address for BIGIP Instance B. IP address parameter must be in the form x.x.x.x. |
| bigIpMgmtAddress01 | No | 10.0.0.11 | string | Management Private IP Address for BIGIP Instance 01. IP address parameter must be in the form x.x.x.x. |
| bigIpMgmtAddress02 | No | 10.0.0.12 | string | Management Private IP Address for BIGIP Instance 02. IP address parameter must be in the form x.x.x.x. |
| bigIpPeerAddr | No | 10.0.1.11 | string | Type the static self IP address of the remote host here. Leave empty if not configuring peering with a remote host on this device. IP address parameter must be in the form x.x.x.x. |
| bigIpRuntimeInitConfig01 | No | https://raw.githubusercontent.com/F5Networks/f5-google-gdm-templates-v2/v2.2.0.0/examples/failover/bigip-configurations/runtime-init-conf-3nic-payg-instance01-with-app.yaml | string | Supply a URL to the bigip-runtime-init configuration file in YAML or JSON format, or an escaped JSON string to use for f5-bigip-runtime-init configuration. |
| bigIpRuntimeInitConfig02 | No | https://raw.githubusercontent.com/F5Networks/f5-google-gdm-templates-v2/v2.2.0.0/examples/failover/bigip-configurations/runtime-init-conf-3nic-payg-instance02-with-app.yaml | string | Supply a URL to the bigip-runtime-init configuration file in YAML or JSON format, or an escaped JSON string to use for f5-bigip-runtime-init configuration. |
| bigIpRuntimeInitPackageUrl | No | https://cdn.f5.com/product/cloudsolutions/f5-bigip-runtime-init/v1.4.1/dist/f5-bigip-runtime-init-1.4.1-1.gz.run | string | Supply a URL to the bigip-runtime-init package. |
| cfeBucket | No | cfe-storage | string | Bucket name used by Cloud Failover Extension. |
| cfeTag | No | bigip_high_availability_solution | string | Cloud Failover deployment tag value. |
| cost | No | f5cost | string | Cost Center Tag. |
| environment | No | f5env | string | Environment Tag. |
| group | No | f5group | string | Group Tag. |
| owner | No | f5owner | string | Owner Tag. |
| provisionPublicIp | No | true | boolean | Provision Public IP address(es) for the BIG-IP Management interface(s). By default, this is set to true. If set to false, the solution will deploy a bastion host instead in order to provide access to the BIG-IP. |
| region | No | us-west1 | string | Google Cloud region used for this deployment, for example 'us-west1'. |
| restrictedSrcAddressApp | Yes |  | array | An IP address range (CIDR) that can be used to restrict access web traffic (80/443) to the BIG-IP instances, for example 'X.X.X.X/32' for a host, '0.0.0.0/0' for the Internet, etc. **NOTE**: The VPC CIDR is automatically added for internal use. |
| restrictedSrcAddressMgmt | Yes |  | array | An IP address range (CIDR) used to restrict SSH and management GUI access to the BIG-IP Management or bastion host instances. **IMPORTANT**: The VPC CIDR is automatically added for internal use (access via bastion host, clustering, etc.). Please restrict the IP address range to your client, for example 'X.X.X.X/32'. Production should never expose the BIG-IP Management interface to the Internet. |
| uniqueString | No | myuniqstr | string | A prefix that will be used to name template resources. Because some resources require globally unique names, we recommend using a unique value. |
| zone | No | us-west1-a | string | Enter the availability zone where you want to deploy the application, for example 'us-west1-a'. |

### Existing Network Template Input Parameters

Note: These are specified in the configuration file. See sample_failover_existing_network.yaml

| Parameter | Required | Default | Type | Description |
| --- | --- | --- | --- | --- |
| application | No | f5app | string | Application Tag. |
| bigIpImageName | No | f5-bigip-16-1-2-2-0-0-28-payg-best-25mbps-220505074742 | string | Name of BIG-IP custom image found in the Google Cloud Marketplace. Example value: `f5-bigip-16-1-2-2-0-0-28-payg-best-25mbps-220505074742`. You can find the names of F5 marketplace images in the README for this template or by running the command: `gcloud compute images list --project f5-7626-networks-public --filter="name~f5"`. |
| bigIpInstanceType | No | n1-standard-4 | string | Instance type assigned to the application, for example 'n1-standard-4'. |
| bigIpExternalSelfIp01 | No | 10.0.1.11 | string | External Private IP Address for BIGIP Instance A. IP address parameter must be in the form x.x.x.x. |
| bigIpExternalSelfIp02 | No | 10.0.1.12 | string | External Private IP Address for BIGIP Instance B. IP address parameter must be in the form x.x.x.x. |
| bigIpInternalSelfIp01 | No | 10.0.2.11 | string | Internal Private IP Address for BIGIP Instance A. IP address parameter must be in the form x.x.x.x. |
| bigIpInternalSelfIp02 | No | 10.0.2.12 | string | Internal Private IP Address for BIGIP Instance B. IP address parameter must be in the form x.x.x.x. |
| bigIpMgmtAddress01 | No | 10.0.0.11 | string | Management Private IP Address for BIGIP Instance 01. IP address parameter must be in the form x.x.x.x. |
| bigIpMgmtAddress02 | No | 10.0.0.12 | string | Management Private IP Address for BIGIP Instance 02. IP address parameter must be in the form x.x.x.x. |
| bigIpPeerAddr | No | 10.0.1.11 | string | Type the static self IP address of the remote host here. Leave empty if not configuring peering with a remote host on this device. IP address parameter must be in the form x.x.x.x. |
| bigIpRuntimeInitConfig01 | No | https://raw.githubusercontent.com/F5Networks/f5-google-gdm-templates-v2/v2.2.0.0/examples/failover/bigip-configurations/runtime-init-conf-3nic-payg-instance01.yaml | --- | Supply a URL to the bigip-runtime-init configuration file in YAML or JSON format, or an escaped JSON string to use for f5-bigip-runtime-init configuration. |
| bigIpRuntimeInitConfig02 | No | https://raw.githubusercontent.com/F5Networks/f5-google-gdm-templates-v2/v2.2.0.0/examples/failover/bigip-configurations/runtime-init-conf-3nic-payg-instance02.yaml | string | Supply a URL to the bigip-runtime-init configuration file in YAML or JSON format, or an escaped JSON string to use for f5-bigip-runtime-init configuration. |
| bigIpRuntimeInitPackageUrl | No | https://cdn.f5.com/product/cloudsolutions/f5-bigip-runtime-init/v1.4.1/dist/f5-bigip-runtime-init-1.4.1-1.gz.run | string | Supply a URL to the bigip-runtime-init package. |
| cfeBucket | No | cfe-storage | string | Bucket name used by Cloud Failover Extension. |
| cfeTag | No | bigip_high_availability_solution | string | Cloud Failover deployment tag value. |
| cost | No | f5cost | string | Cost Center Tag. |
| environment | No | f5env | string | Environment Tag. |
| group | No | f5group | string | Group Tag. |
| owner | No | f5owner | string | Owner Tag. |
| networks | Yes |  | Object | Networks object which provides names for mgmt and app networks |
| networks.externalNetworkName | Yes |  | string | External network name |
| networks.interlanNetworkName | No |  | string | Internal network name |  
| networks.mgmtNetworkName | No |  | string | Management network name | 
| provisionPublicIp | No | false | boolean | Provision Public IP address(es) for the BIG-IP Management interface(s). By default, this is set to true. If set to false, the solution will deploy a bastion host instead in order to provide access to the BIG-IP. |
| region | No | us-west1 | string | Google Cloud region used for this deployment, for example 'us-west1'. |
| restrictedSrcAddressApp | Yes |  | array | An IP address range (CIDR) that can be used to restrict access web traffic (80/443) to the BIG-IP instances, for example 'X.X.X.X/32' for a host, '0.0.0.0/0' for the Internet, etc. **NOTE**: The VPC CIDR is automatically added for internal use. |
| restrictedSrcAddressMgmt | Yes |  | array | An IP address range (CIDR) used to restrict SSH and management GUI access to the BIG-IP Management or bastion host instances. Provide a YAML list of addresses or networks in CIDR notation, for example, '- 55.55.55.55/32' for a host, '- 10.0.0.0/8' for a network, etc. NOTE: If using a Bastion Host (when ProvisionPublicIp = false), you must also include the Bastion's source network, for example '- 10.0.0.0/8'. **IMPORTANT**: The VPC CIDR is automatically added for internal use (access via bastion host, clustering, etc.). Please restrict the IP address range to your client, for example '- X.X.X.X/32'. Production should never expose the BIG-IP Management interface to the Internet. |
| subnets | Yes |  | object | Subnet object which provides names for mgmt and app subnets |
| subnets.appSubnetName | Yes |  | string | Management subnet name |
| subnets.internalSubnetName | Yes |  | string | Internal subnet name |  
| subnets.mgmtSubnetName | Yes |  | string | Management subnet name | 
| uniqueString | No | myuniqstr | string | A prefix that will be used to name template resources. Because some resources require globally unique names, we recommend using a unique value. |
| zone | No | us-west1-a | string | Enter the availability zone where you want to deploy the application, for example 'us-west1-a'. |



### Template Outputs

| Name | Required Resource | Type | Description | 
| --- | --- | --- | --- |
| appInstanceName |  | string | Application server instance name. |
| appPrivateIp |  | string | Application server private IP address. |
| appPublicIp |  | string | Application server public IP address. |
| appUsername |  | string | Application server user name. |
| bastionInstanceId |  | string | Bastion instance ID. |
| bastionPublicIp |  | string | Bastion public IP address. |
| bastionPublicSsh |  | string | Bastion SSH command. |
| bigIpInstanceId1 |  | string | BIG-IP instance ID. |
| bigIpInstanceId2 |  | string | BIG-IP instance ID. |
| bigIpInstanceName1 |  | string | BIG-IP instance name. |
| bigIpInstanceName2 |  | string | BIG-IP instance name. |
| bigIpManagementPrivateIp1 |  | string | BIG-IP management private IP address. |
| bigIpManagementPrivateIp2 |  | string | BIG-IP management private IP address. |
| bigIpManagementPrivateUrl1 |   | string |BIG-IP management private IP URL. |
| bigIpManagementPrivateUrl2 |  | string | BIG-IP management private IP URL. |
| bigIpManagementPublicIp1 |  | string | BIG-IP management public IP address. |
| bigIpManagementPublicIp2 |  | string | BIG-IP management public IP address. |
| bigIpManagementPublicSsh1 |  | string | BIG-IP management SSH command. |
| bigIpManagementPublicSsh2 |  | string | BIG-IP management SSH command. |
| bigIpManagementPublicUrl1 |  | string | BIG-IP management public IP URL. |
| bigIpManagementPublicUrl2 |  | string | BIG-IP management public IP URL. |
| deploymentName |  | string | Quickstart deployment name. |
| networkName0 |  | string | Management network name. |
| networkName1 |  | string | External network name. |
| networkName2 |  | string | Internal network name. |
| networkSelfLink0 |  | string | Management network self link. |
| networkSelfLink1 |  | string | External network self link. |
| networkSelfLink2 |  | string | Internal network self link. |
| vip1PrivateIp1 |  | string | Virtual Server private IP address. |
| vip1PrivateIp2 |  | string | Virtual Server private IP address. |
| vip1PrivateUrlHttp1 |  | string | Virtual Server private HTTP URL. |
| vip1PrivateUrlHttp2 |  | string | Virtual Server private HTTP URL. |
| vip1PrivateUrlHttps1 |  | string | Virtual Server private HTTPS URL. |
| vip1PrivateUrlHttps2 |  | string | Virtual Server private HTTPS URL. |
| vip1PublicIp1 |  | string | Virtual Server public IP address. |
| vip1PublicIp2 |  | string | Virtual Server public IP address. |
| vip1PublicUrlHttp1 |  | string | Virtual Server public HTTP URL. |
| vip1PublicUrlHttp2 |  | string | Virtual Server public HTTP URL. |
| vip1PublicUrlHttps1 |  | string | Virtual Server public HTTPS URL. |
| vip1PublicUrlHttps2 |  | string | Virtual Server public HTTPS URL. |


### Existing Network Template Outputs


| Name | Required Resource | Type | Description | 
| --- | --- | --- | --- |
| bigIpInstanceId1 |  | string | BIG-IP instance ID. |
| bigIpInstanceId2 |  | string | BIG-IP instance ID. |
| bigIpInstanceName1 |  | string | BIG-IP instance name. |
| bigIpInstanceName2 |  | string | BIG-IP instance name. |
| bigIpManagementPrivateIp1 |  | string | BIG-IP management private IP address. |
| bigIpManagementPrivateIp2 |  | string | BIG-IP management private IP address. |
| bigIpManagementPrivateUrl1 |  | string | BIG-IP management private IP URL. |
| bigIpManagementPrivateUrl2 |  | string | BIG-IP management private IP URL. |
| bigIpManagementPublicIp1 |  | string | BIG-IP management public IP address. |
| bigIpManagementPublicIp2 |  | string | BIG-IP management public IP address. |
| bigIpManagementPublicSsh1 |   | string |BIG-IP management SSH command. |
| bigIpManagementPublicSsh2 |  | string | BIG-IP management SSH command. |
| bigIpManagementPublicUrl1 |  | string | BIG-IP management public IP URL. |
| bigIpManagementPublicUrl2 |  | string | BIG-IP management public IP URL. |
| deploymentName |   | string |Quickstart deployment name. |
| vip1PrivateIp1 |  | string | Virtual Server private IP address. |
| vip1PrivateIp2 |  | string | Virtual Server private IP address. |
| vip1PrivateUrlHttp1 |  | string | Virtual Server private HTTP URL. | 
| vip1PrivateUrlHttp2 |  | string | Virtual Server private HTTP URL. |
| vip1PrivateUrlHttps1 |  | string | Virtual Server private HTTPS URL. |
| vip1PrivateUrlHttps2 |  | string | Virtual Server private HTTPS URL. |
| vip1PublicIp1 |  | string | Virtual Server public IP address. |
| vip1PublicIp2 |  | string | Virtual Server public IP address. |
| vip1PublicUrlHttp1 |  | string | Virtual Server public HTTP URL. |
| vip1PublicUrlHttp2 |  | string | Virtual Server public HTTP URL. |
| vip1PublicUrlHttps1 |  | string | Virtual Server public HTTPS URL. |
| vip1PublicUrlHttps2 |  | string | Virtual Server public HTTPS URL. |

## Deploying this Solution

See [Prerequisites](#prerequisites).

To deploy this solution, you must use the [gcloud CLI](#deploying-via-the-gcloud-cli)

### Deploying via the gcloud CLI

To deploy the BIG-IP VE from the parent template YAML file, use the following command syntax:

```bash
gcloud deployment-manager deployments create ${DEPLOYMENT_NAME} --config ${CONFIG_FILE}
```

Keep in mind the following:

- Follow the sample_failover.yaml file for guidance on what to include in the yaml *CONFIG_FILE*, include required imports and parameters
- *DEPLOYMENT_NAME*<br>This name must be unique.<br>
- *CONFIG_FILE*<br>If your file is not in the same directory as where running the command, include the full file path in the command.

### Changing the BIG-IP Deployment

You will most likely want or need to change the BIG-IP configuration. This generally involves referencing or customizing a [F5 BIG-IP Runtime Init](https://github.com/F5Networks/f5-bigip-runtime-init) configuration file and passing it through the **bigIpRuntimeInitConfig01** and **bigIpRuntimeInitConfig02** template parameters as a URL.

Example from sample_failover.yaml:

```yaml
    ### (OPTIONAL) Supply a URL to the bigip-runtime-init configuration file in YAML or JSON format
    bigIpRuntimeInitConfig01: https://raw.githubusercontent.com/F5Networks/f5-google-gdm-templates-v2/v2.2.0.0/examples/failover/bigip-configurations/runtime-init-conf-3nic-payg-instance01.yaml
    bigIpRuntimeInitConfig02: https://raw.githubusercontent.com/F5Networks/f5-google-gdm-templates-v2/v2.2.0.0/examples/failover/bigip-configurations/runtime-init-conf-3nic-payg-instance02.yaml
```

**IMPORTANT**: Note the "raw.githubusercontent.com". Any URLs pointing to github **must** use the raw file format.

F5 has provided the following example configuration files in the `examples/failover/bigip-configurations` folder:

- These examples install Automation Tool Chain packages for a PAYG licensed deployment.
  - `runtime-init-conf-3nic-payg-instance01.yaml`
  - `runtime-init-conf-3nic-payg-instance02.yaml`
- These examples install Automation Tool Chain packages and create WAF-protected services for a PAYG licensed deployment.
  - `runtime-init-conf-3nic-payg-instance01-with-app.yaml`
  - `runtime-init-conf-3nic-payg-instance02-with-app.yaml`
- These examples install Automation Tool Chain packages for a BYOL licensed deployment.
  - `runtime-init-conf-3nic-byol-instance01.yaml`
  - `runtime-init-conf-3nic-byol-instance02.yaml`
- These examples install Automation Tool Chain packages and create WAF-protected services for a BYOL licensed deployment.
  - `runtime-init-conf-3nic-byol-instance01-with-app.yaml`
  - `runtime-init-conf-3nic-byol-instance02-with-app.yaml`
- `Rapid_Deployment_Policy_13_1.xml` - This ASM security policy is supported for BIG-IP 13.1 and later.

See [F5 BIG-IP Runtime Init](https://github.com/F5Networks/f5-bigip-runtime-init) for more examples.

By default, this solution deploys 3NIC BIG-IP instances using these examples:
  - `runtime-init-conf-3nic-payg-instance01.yaml`
  - `runtime-init-conf-3nic-payg-instance02.yaml`

- When specifying values for the bigIpInstanceType parameter, ensure that the instance type you select is appropriate for the 3 NIC deployment scenario. See [Google Machine Families](https://cloud.google.com/compute/docs/machine-types) for more information.

However, most changes require modifying the configurations themselves. For example:

To deploy a **BYOL** instance:

1. Edit/modify the Declarative Onboarding (DO) declaration in the corresponding `byol` runtime-init config files with the new `regKey` value.

Example:

```yaml
My_License:
  class: License
  licenseType: regKey
  regKey: AAAAA-BBBBB-CCCCC-DDDDD-EEEEEEE
```

2. Publish/host the customized runtime-init config file at a location reachable by the BIG-IP at deploy time (for example: github, Google Storage, etc.)
3. Update the **bigIpRuntimeInitConfig01** and **bigIpRuntimeInitConfig02** input parameters to reference the new URLs of the updated configurations.
4. Update the **bigIpImageName** input parameter to use `byol` image.  (gcloud compute images list --project f5-7626-networks-public --filter="name~byol").
   Example:
   ```yaml
   bigIpImageName: f5-bigip-16-1-2-2-0-0-28-byol-all-modules-2boot-loc-0505081937
   ```

In order deploy additional **virtual services**:

For illustration purposes, this solution pre-provisions IP addresses and the runtime-init configurations contain an AS3 declaration to create an example virtual service. However, in practice, cloud-init runs once and is typically used for initial provisioning, not as the primary configuration API for a long-running platform. More typically in an infrastructure use case, virtual services are not included in the initial cloud-init configuration are added post initial deployment which involves:

1. _Cloud_ - Provisioning additional Services. Examples:
   - Private Virtual Services on Alias IP Ranges: [gcloud compute instances network-interfaces update](https://cloud.google.com/vpc/docs/configure-alias-ip-ranges#adding_alias_ip_ranges_to_an_existing_instance)
   - Public Virtual Services with Forwarding Rules: [gcloud compute forwarding-rules create](https://cloud.google.com/sdk/gcloud/reference/compute/forwarding-rules/create)
2. _BIG-IP_ - Creating Virtual Services that match those additional Services
   - Updating the [AS3](https://clouddocs.f5.com/products/extensions/f5-appsvcs-extension/latest/userguide/composing-a-declaration.html) declaration with additional Virtual Services (see **virtualAddresses:**).

_NOTE: For cloud resources, templates can be customized to pre-provision and update additional resources (for example: various combinations of NICs, forwarding rules, alias addresses, IAM roles, etc.). Please see [Getting Help](#getting-help) for more information. For BIG-IP configurations, you can leverage any REST or Automation Tool Chain clients like [Ansible](https://ansible.github.io/workshops/exercises/ansible_f5/3.0-as3-intro/),[Terraform](https://registry.terraform.io/providers/F5Networks/bigip/latest/docs/resources/bigip_as3),etc._

## Validation

This section describes how to validate the template deployment, test the WAF service, and troubleshoot common problems.

### Validating the Deployment

To view the status of the example and module template deployments, navigate to **Deployment Manager > _Deployments_ > _Deployment Name_**. You should see a series of deployments, including one each for the example template as well as the application, network, dag, and bigip templates. The deployment status for the parent template deployment should indicate that the template has been successfully deployed.

Expected Deploy time for entire stack =~ 8-10 minutes.

If any of the deployments are in a failed state, proceed to the [Troubleshooting Steps](#troubleshooting-steps) section below.

### Accessing the BIG-IP

- NOTE:
  - The following CLI commands require the gcloud CLI and yq: https://github.com/mikefarah/yq#install
  - When **false** is selected for **provisionPublicIp**, you must connect to the BIG-IP instance(s) via a bastion host. Once connected to the bastion host, you may then connect via SSH to the private Management IP address of the BIG-IP instances. The default username is **admin** and the default password is the value of the Google Secrets Manager secret provided in the runtime init BIGIP_PASSWORD runtime parameter.

From Parent Template Outputs:
  - **Console**:  Navigate to **Deployment Manager > Deployments > *DEPLOYMENT_NAME* > Overview > Layout > Resources > Outputs**.
  - **Google CLI**:
    ```bash
    gcloud deployment-manager manifests describe --deployment=${DEPLOYMENT_NAME} --format="value(layout)" | yq .resources[0].outputs
    ```

- Obtain the IP address of the first BIG-IP Management Port (To connect to the second BIG-IP instance, repeat these steps using the appropriate output names):
  - **Console**: Navigate to **Deployment Manager > Deployments > *DEPLOYMENT_NAME* > Overview > Layout > Resources > Outputs > *bigIpManagementPublicIp1***.
  - **Google CLI**: 
    ``` bash 
    gcloud deployment-manager manifests describe --deployment=${DEPLOYMENT_NAME} --format="value(layout)" | yq '.resources[0].outputs[] | select(.name | contains("bigIpManagementPublicIp1")).finalValue'
    ```

OR if you are going through a bastion host (when **provisionPublicIP** = **false**):

- Obtain the Public IP address of the bastion host:
  - **Console**: Navigate to **Deployment Manager > Deployments > *DEPLOYMENT_NAME* > Overview > Layout > Resources > Outputs > bastionPublicIp**.
  - **gcloud CLI**:
    ```bash
    gcloud deployment-manager manifests describe --deployment=${DEPLOYMENT_NAME} --format="value(layout)" | yq '.resources[0].outputs[] | select(.name | contains("bastionPublicIp")).finalValue'
    ```

- Obtain the Private IP address of the first BIG-IP Management Port = nic1 :
  - **Console**: Navigate to **Deployment Manager > Deployments > *DEPLOYMENT_NAME* > Overview > Layout > Resources > Outputs > bigIpManagementPrivateIp1**.
  - **gcloud CLI**:
    ```bash
    gcloud deployment-manager manifests describe --deployment=${DEPLOYMENT_NAME} --format="value(layout)" | yq '.resources[0].outputs[] | select(.name | contains("bigIpManagementPrivateIp1")).finalValue'
    ```

#### SSH

- **SSH Key authentication**:
  ```bash
  ssh admin@${IP_ADDRESS_FROM_OUTPUT} -i ${YOUR_PRIVATE_SSH_KEY}
  ```

- **SSH Password authentication**:
  ```bash
  ssh admin@${IP_ADDRESS_FROM_OUTPUT}
  ```
  At prompt, enter the value of the Google Secrets Manager secret provided in the runtime init BIGIP_PASSWORD runtime parameter.


- OR if you are going through a bastion host (when **provisionPublicIP** = **false**):

    From your desktop client/shell, create an SSH tunnel:
    ```bash
    ssh -i [PROJECT_USER_PRIVATE_KEY] -o ProxyCommand='ssh -i [PROJECT_USER_PRIVATE_KEY] -W %h:%p [PROJECT_USER]@[BASTION-HOST-PUBLIC-IP]' admin@[BIG-IP-MGMT-PRIVATE-IP]
    ```

    Replace the variables in brackets before submitting the command.

    For example:
    ```bash
    ssh -i ~/.ssh/mykey.pem -o ProxyCommand='ssh -i ~/.ssh/mykey.pem -W %h:%p myprojectuser@34.82.102.190' admin@10.0.0.2
    ```
#### WebUI

- Obtain the IP address of the BIG-IP Management Port:

  - See 'Obtain the public IP address of the BIG-IP Management Port' section above:
  - By default, the Management URL will be `https://${MANAGEMENT-IP}/`

  - OR when you are going through a bastion host (when **provisionPublicIP** = **false**):

    From your desktop client/shell, create an SSH tunnel:
    ```bash
    ssh -i [PROJECT_USER_PRIVATE_KEY] [PROJECT_USER]@[BASTION-HOST-PUBLIC-IP] -L 8443:[BIG-IP-MGMT-PRIVATE-IP]:[BIGIP-GUI-PORT]
    ```
    For example:
    ```bash
    ssh -i ~/.ssh/mykey.pem myprojectuser@34.82.102.190 -L 8443:10.0.0.2:443
    ```

    You should now be able to open a browser to the BIG-IP UI from your desktop:

    https://localhost:8443


- Open a browser to the Management URL:
  - NOTE: By default, the BIG-IP's WebUI starts with a self-signed cert. Follow your browsers instructions for accepting self-signed certs (for example, if using Chrome, click inside the page and type this "thisisunsafe". If using Firefox, click "Advanced" button, Click "Accept Risk and Continue").
  - Provide
    - username: admin
    - password: Enter the value of the Google Secrets Manager secret provided in the runtime init BIGIP_PASSWORD runtime parameter.

### Further Exploring

#### WebUI

 - Navigate to **Local Traffic > Virtual Servers**. In upper right corner, select Partition = `Tenant_1`
 - You should now see two Virtual Services (one for HTTP and one for HTTPS). They should show up as Green. Click on them to look at the configuration *(declared in the AS3 declaration)*

#### SSH

  - From tmsh shell, type 'bash' to enter the bash shell:
    - Examine BIG-IP configuration via [F5 Automation Toolchain](https://www.f5.com/pdf/products/automation-toolchain-overview.pdf) declarations:
    ```bash
    curl -u admin: http://localhost:8100/mgmt/shared/declarative-onboarding | jq .
    ```
    - If you deployed the example application (**provisionExampleApp** = **true**), examine the Application Services declaration:
    ```bash
    curl -u admin: http://localhost:8100/mgmt/shared/appsvcs/declare | jq .
    ```
    - Exampine the BIG-IP [Cloud Failover Extension (CFE)](https://clouddocs.f5.com/products/extensions/f5-cloud-failover/latest/) declaration:
    ```bash
    curl -su admin: http://localhost:8100/mgmt/shared/cloud-failover/declare | jq . 
    ```
    - Examine the [Runtime-Init](https://github.com/F5Networks/f5-bigip-runtime-init) Config downloaded: 
    ```bash 
    cat /config/cloud/runtime-init.conf
    ```

### Testing the WAF Service

To test the WAF service (if deploying using runtime-init-conf-*-with-app.yaml), perform the following steps:

- Obtain the IP address of the WAF service:
  - **Console**: Navigate to **Deployment Manager > Deployments > *DEPLOYMENT_NAME* > Overview > Layout > Resources > Outputs  > vip1PublicIp1**.
  - **Google CLI**: 
      ```bash
      gcloud deployment-manager manifests describe --deployment=${DEPLOYMENT_NAME} --format="value(layout)" | yq '.resources[0].outputs[] | select(.name | contains("vip1PublicIp1")).finalValue'
      ```

- Verify the application is responding:
  - Paste the IP address in a browser: `https://${IP_ADDRESS_FROM_OUTPUT}`
    - NOTE: By default, the Virtual Service starts with a self-signed cert. Follow your browsers instructions for accepting self-signed certs (for example, if using Chrome, click inside the page and type this "thisisunsafe". If using Firefox, click the "Advanced" button, click "Accept Risk and Continue", etc.).
  - Use curl:
    ```shell
     curl -sko /dev/null -w '%{response_code}\n' https://${IP_ADDRESS_FROM_OUTPUT}
    ```
- Verify the WAF is configured to block illegal requests:
  ```shell
  curl -sk -X DELETE https://${IP_ADDRESS_FROM_OUTPUT}
  ```
  - The response should include a message that the request was blocked, and a reference support ID
    Example:
    ```shell
    $ curl -sko /dev/null -w '%{response_code}\n' https://55.55.55.55
    200
    $ curl -sk -X DELETE https://55.55.55.55
    <html><head><title>Request Rejected</title></head><body>The requested URL was rejected. Please consult with your administrator.<br><br>Your support ID is: 2394594827598561347<br><br><a href='javascript:history.back();'>[Go Back]</a></body></html>
    ```

### Testing Failover

 When **provisionExampleApp** is **true**, to test failover, perform the following steps:

1. Log on the BIG-IPs per instructions above:

  - **WebUI**: Go to Device Management of Active Instance -> Traffic-Groups -> Select box next to *traffic-group-1* -> Click the "Force to Standby" button *.
  - **BIG-IP CLI**: 
      ```bash 
      tmsh run sys failover standby
      ```

Verify the Virtual Service (**vip1PublicIp**) is remapped to the peer BIG-IP target instance after failover. 
  - **Console**: Navigate to  **Network Services > Load Balancing > Go to the Advanced view by clicking on "load balancing components view" link > *fwrule1* > Target**
  - **gcloud CLI** 
      ```bash 
      gcloud compute forwarding-rules list
      ```

For information on the Cloud Failover solution, see [F5 Cloud Failover Extension](https://clouddocs.f5.com/products/extensions/f5-cloud-failover/latest/userguide/gcp.html).


## Deleting this Solution


As Google Deployment Manager does not delete storage buckets that contain data, in order to delete this deployment, you will first need to manually empty and/or delete the storage bucket created for the Cloud Failover Extension (provided via *cfeBucket* parameter). Go to *Google Cloud Console -> S3* and search for *cfeBucket* bucket name, select the box associated with it and then click the "Delete" button. 

You can now delete the deployment.

### Deleting the deployment via Google Cloud Console

1. Navigate to **Deployment Manager** > Select "Deployments" Icon.

2. Select your parent template deployment by clicking the check box next to the deployment name.

3. Click **Delete**.

4. Choose an option for retaining template resources.

5. Click **Delete All** to confirm.

### Deleting the deployment using the gcloud CLI

```bash
gcloud deployment-manager deployments delete ${DEPLOYMENT_NAME} -q
```

## Troubleshooting Steps

There are generally two classes of issues:

1. Template deployment itself failed
2. Resource(s) within the template failed to deploy

To verify that all templates deployed successfully, follow the instructions under **Validating the Deployment** above to locate the failed deployment(s).

Click on the name of a failed deployment and then click **Events**. Click the link in the red banner at the top of the deployment overview for details about the failure cause.

Additionally, if the template passed validation but individual template resources have failed to deploy, you can see more information by expanding Deployment Details, then clicking on the Operation details column for the failed resource. **When creating a GitHub issue for a template, please include as much information as possible from the failed Google deployment/resource events.**

Common deployment failure causes include:

- Required fields were left empty or contained incorrect values (input type mismatch, prohibited characters, malformed YAML, etc.) causing template validation failure.
- Insufficient permissions to create the deployment or resources created by a deployment.
- Resource limitations (exceeded limit of IP addresses or compute resources, etc.).
- Google service issues (these will usually surface as 503 internal server errors in the deployment status error message).

If all deployments completed "successfully" but maybe the BIG-IP or Service is not reachable, then log in to the BIG-IP instance via SSH to confirm BIG-IP deployment was successful (for example, if startup scripts completed as expected on the BIG-IP). To verify BIG-IP deployment, perform the following steps:

- Obtain the IP address of the BIG-IP instance. See instructions [above](#accessing-the-bigip-ip)
- Check startup-script to make sure was installed/interpolated correctly:
  - `cat /config/cloud/runtime-init.conf`
- Check the logs (in order of invocation):
  - cloud-agent logs:
    - _/var/log/boot.log_
    - _/var/log/cloud-init.log_
    - _/var/log/cloud-init-output.log_
  - runtime-init Logs:
    - _/var/log/cloud/startup-script.log_: This file contains events that happen prior to execution of f5-bigip-runtime-init. If the files required by the deployment fail to download, for example, you will see those events logged here.
    - _/var/log/cloud/bigipRuntimeInit.log_: This file contains events logged by the f5-bigip-runtime-init onboarding utility. If the configuration is invalid causing onboarding to fail, you will see those events logged here. If deployment is successful, you will see an event with the body "All operations completed successfully".
  - Automation Tool Chain Logs:
    - _/var/log/restnoded/restnoded.log_: This file contains events logged by the F5 Automation Toolchain components. If an Automation Toolchain declaration fails to deploy, you will see more details for those events logged here.
- _GENERAL LOG TIP_: Search most critical error level errors first (for example, egrep -i err /var/log/<Logname>).

If you are unable to login to the BIG-IP instance(s), you can navigate to **Compute Engine > VM Instances > _uniqueString_-bigip1 > Serial port 1 (console)** to investigate any potential details from the serial console.

## Security

This GDM template downloads helper code to configure the BIG-IP system:

- f5-bigip-runtime-init.gz.run: The self-extracting installer for the F5 BIG-IP Runtime Init RPM can be verified against a SHA256 checksum provided as a release asset on the F5 BIG-IP Runtime Init public GitHub repository, for example: https://github.com/F5Networks/f5-bigip-runtime-init/releases/download/1.3.2/f5-bigip-runtime-init-1.3.2-1.gz.run.sha256.
- F5 BIG-IP Runtime Init: The self-extracting installer script extracts, verifies, and installs the F5 BIG-IP Runtime Init RPM package. Package files are signed by F5 and automatically verified using GPG.
- F5 Automation Toolchain components: F5 BIG-IP Runtime Init downloads, installs, and configures the F5 Automation Toolchain components. Although it is optional, F5 recommends adding the extensionHash field to each extension install operation in the configuration file. The presence of this field triggers verification of the downloaded component package checksum against the provided value. The checksum values are published as release assets on each extension's public GitHub repository, for example: https://github.com/F5Networks/f5-appsvcs-extension/releases/download/v3.18.0/f5-appsvcs-3.18.0-4.noarch.rpm.sha256

The following configuration file will verify the Declarative Onboarding and Application Services extensions before configuring AS3 from a local file:

```yaml
runtime_parameters: []
extension_packages:
  install_operations:
    - extensionType: do
      extensionVersion: 1.19.0
      extensionHash: 15c1b919954a91b9ad1e469f49b7a0915b20de494b7a032da9eb258bbb7b6c49
    - extensionType: as3
      extensionVersion: 3.26.0
      extensionHash: b33a96c84b77cff60249b7a53b6de29cc1e932d7d94de80cc77fb69e0b9a45a0
extension_services:
  service_operations:
    - extensionType: as3
      type: url
      value: file:///examples/declarations/as3.json
```

More information about F5 BIG-IP Runtime Init and additional examples can be found in the [GitHub repository](https://github.com/F5Networks/f5-bigip-runtime-init/blob/main/README.md).

If you want to verify the integrity of the template itself, F5 provides checksums for all of our templates. For instructions and the checksums to compare against, see [checksums-for-f5-supported-cft-and-arm-templates-on-github](https://community.f5.com/t5/crowdsrc/checksums-for-f5-supported-cloud-templates-on-github/ta-p/284471).

List of endpoints BIG-IP may contact during onboarding:

- BIG-IP image default:
  - vector2.brightcloud.com (by BIG-IP image for [IPI subscription validation](https://support.f5.com/csp/article/K03011490) )
- Solution / Onboarding:
  - github.com (for downloading helper packages mentioned above)
  - f5-cft.s3.amazonaws.com (downloading GPG Key and other helper configuration files)
  - license.f5.com (licensing functions)
- Telemetry:
  - www-google-analytics.l.google.com
  - product-s.apis.f5.com.
  - f5-prod-webdev-prod.apigee.net.
  - id-prod-global-endpoint.trafficmanager.net.

## BIG-IP Versions

These templates have been tested and validated with the following versions of BIG-IP.

| Google BIG-IP Image Version | BIG-IP Version         |
| --------------------------- | ---------------------- |
| 16.1.200000                 | 16.1.2.1 Build 0.0.10  |
| 14.1.400000                 | 14.1.4.4 Build 0.0.4   |

**Note**: Due to an issue (ID 1013209) with the default ca-bundle, you may not host F5 BIG-IP Runtime Init configuration files in a Google Storage bucket when deploying BIG-IP v14 images.

## Supported Instance Types and Hypervisors

- For a list of supported Google instance types for this solution, see the [Google instances for BIG-IP VE](https://clouddocs.f5.com/cloud/public/v1/google/Google_singleNIC.html).

- For a list of versions of the BIG-IP Virtual Edition (VE) and F5 licenses that are supported on specific hypervisors and Google Cloud, see [supported-hypervisor-matrix](https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/ve-supported-hypervisor-matrix.html).

## Documentation

For more information on F5 solutions for Google Cloud, including manual configuration procedures for some deployment scenarios, see the Google Cloud section of [Public Cloud Docs](http://clouddocs.f5.com/cloud/public/v1/).

## Getting Help

Due to the heavy customization requirements of external cloud resources and BIG-IP configurations in these solutions, F5 does not provide technical support for deploying, customizing, or troubleshooting the templates themselves. However, the various underlying products and components used (for example: [F5 BIG-IP Virtual Edition](https://clouddocs.f5.com/cloud/public/v1/), [F5 BIG-IP Runtime Init](https://github.com/F5Networks/f5-bigip-runtime-init), [F5 Automation Toolchain](https://www.f5.com/pdf/products/automation-toolchain-overview.pdf) extensions, and [Cloud Failover Extension (CFE)](https://clouddocs.f5.com/products/extensions/f5-cloud-failover/latest/)) in the solutions located here are F5-supported and capable of being deployed with other orchestration tools. Read more about [Support Policies](https://www.f5.com/company/policies/support-policies). Problems found with the templates deployed as-is should be reported via a GitHub issue.

For help with authoring and support for custom CST2 templates, we recommend engaging F5 Professional Services (PS).

### Filing Issues

Use the **Issues** link on the GitHub menu bar in this repository for items such as enhancement or feature requests and bugs found when deploying the example templates as-is. Tell us as much as you can about what you found and how you found it.
