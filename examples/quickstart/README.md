# Deploying the BIG-IP VE in Google - Example Quickstart BIG-IP WAF (LTM + ASM) - Virtual Machine

[![Releases](https://img.shields.io/github/release/F5Networks/f5-google-gdm-templates-v2.svg)](https://github.com/F5Networks/f5-google-gdm-templates-v2/releases)
[![Issues](https://img.shields.io/github/issues/F5Networks/f5-google-gdm-templates-v2.svg)](https://github.com/F5Networks/f5-google-gdm-templates-v2/issues)

## Contents

- [Deploying the BIG-IP VE in Google - Example Quickstart BIG-IP WAF (LTM + ASM) - Virtual Machine](#deploying-the-big-ip-ve-in-google---example-quickstart-big-ip-waf-ltm--asm---virtual-machine)
  - [Contents](#contents)
  - [Introduction](#introduction)
  - [Diagram](#diagram)
  - [Prerequisites](#prerequisites)
  - [Important Configuration Notes](#important-configuration-notes)
    - [Template Input Parameters](#template-input-parameters)
    - [Template Outputs](#template-outputs)
  - [Deploying this Solution](#deploying-this-solution)
    - [Deploying via the Google CLI](#deploying-via-the-gcloud-cli)
    - [Changing the BIG-IP Deployment](#changing-the-big-ip-deployment)
  - [Validation](#validation)
    - [Validating the Deployment](#validating-the-deployment)
    - [Accessing the BIG-IP](#accessing-the-big-ip)
      - [SSH](#ssh)
      - [WebUI](#webui)
    - [Further Exploring](#further-exploring)
      - [WebUI](#webui-1)
      - [SSH](#ssh-1)
    - [Testing the WAF Service](#testing-the-waf-service)
  - [Customizing this Solution](#cloud-configuration)
  - [Deleting this Solution](#deleting-this-solution)
    - [Deleting the deployment via Google Portal](#deleting-the-deployment-via-google-cloud-console)
    - [Deleting the deployment using the Google CLI](#deleting-the-deployment-using-the-gcloud-cli)
  - [Troubleshooting Steps](#troubleshooting-steps)
  - [Security](#security)
  - [BIG-IP Versions](#big-ip-versions)
  - [Supported Instance Types and Hypervisors](#supported-instance-types-and-hypervisors)
  - [Documentation](#documentation)
  - [Getting Help](#getting-help)
    - [Filing Issues](#filing-issues)


## Introduction

The goal of this solution is to reduce prerequisites and complexity to a minimum so with a few clicks, a user can quickly deploy a BIG-IP, login and begin exploring the BIG-IP platform in a working full-stack deployment capable of passing traffic. 

This solution uses a parent template to launch several linked child templates (modules) to create a full example stack for the BIG-IP. The linked templates are located in the `examples/modules` directory in this repository. *F5 recommends cloning this repository and modifying these templates to fit your use case.*


The modules below create the following cloud resources:

- **Network**: This template creates Google networks and subnets.
- **Application**: This template creates a generic example application for use when demonstrating live traffic through the BIG-IP instance.
- **Disaggregation** *(DAG/Ingress)*: This template creates resources required to get traffic to the BIG-IP, including firewall rules.
- **BIG-IP**: This template creates a BIG-IP VM instance provisioned with Local Traffic Manager (LTM) and Application Security Manager (ASM). 

By default, this solution creates a VNet with four subnets, an example Web Application instance and a PAYG BIG-IP instance with three network interfaces (one for management and two for dataplane/application traffic - called external and internal). Application traffic from the Internet traverses an external network interface configured with both public and private IP addresses. Traffic to the application traverses an internal network interface configured with a private IP address.

***DISCLAIMER/WARNING***: To reduce prerequisites and complexity to a bare minimum for evaluation purposes only, this quickstart provides immediate access to the management interface via a Public IP. At the very *minimum*, configure the **restrictedSrcAddressMgmt** parameter to limit access to your client IP or trusted network. In production deployments, management access should never be directly exposed to the Internet and instead should be accessed via typical management best practices like jumpboxes/bastion hosts, VPNs, etc.


## Diagram

![Configuration Example](diagram.png)

## Prerequisites

  - You must have installed the [Google Cloud SDK](https://cloud.google.com/sdk/downloads)
  - This solution requires a Google Cloud account that can provision objects described in the solution using the gcloud CLI:
      ```bash
      gcloud deployment-manager deployments create ${DEPLOYMENT_NAME} --template ${TEMPLATE_FILE} --properties ${PROPERTIES}
      ```
  - This solution requires an [SSH key](https://cloud.google.com/compute/docs/instances/adding-removing-ssh-keys) for access to the BIG-IP instances.
  - This solution requires you to accept any Google Cloud Marketplace "License/Terms and Conditions" for the images used in this solution.
    - By default, this solution uses [F5 Advanced WAF with LTM, IPI and TC (PAYG - 25Mbps)](https://console.cloud.google.com/marketplace/product/f5-7626-networks-public/f5-big-awf-plus-pve-payg-25mbps)


## Important Configuration Notes

- By default, this solution creates a username **quickstart** with a **temporary** password set to value of the Google virtual machine ID which is provided in the output **bigIpVmId** of the parent template. **IMPORTANT**: You should change this temporary password immediately following deployment. Alternately, you may remove the quickstart user class from the runtime-init configuration prior to deployment to prevent this user account from being created. See [Changing the BIG-IP Deployment](#changing-the-big-ip-deployment) for more details.

- This solution requires Internet access for: 
  1. Downloading additional F5 software components used for onboarding and configuring the BIG-IP (via github.com). Internet access is required via the management interface and then via a dataplane interface (for example, external Self-IP) once a default route is configured. See [Overview of Mgmt Routing](https://support.f5.com/csp/article/K13284) for more details. By default, as a convenience, this solution provisions Public IPs to enable this but in a production environment, outbound access should be provided by a `routed` SNAT service (for example: Cloud NAT, custom firewall, etc.). *NOTE: access via web proxy is not currently supported. Other options include 1) hosting the file locally and modifying the runtime-init package url and configuration files to point to local URLs instead or 2) baking them into a custom image, using the [F5 Image Generation Tool](https://clouddocs.f5.com/cloud/public/v1/ve-image-gen_index.html).*
  2. Contacting native cloud services for various cloud integrations: 
    - *Onboarding*:
        - [F5 BIG-IP Runtime Init](https://github.com/F5Networks/f5-bigip-runtime-init) - to fetch secrets from native vault services
    - *Operation*:
        - [F5 Application Services 3](https://clouddocs.f5.com/products/extensions/f5-appsvcs-extension/latest/) - for features like Service Discovery
        - [F5 Telemetry Streaming](https://clouddocs.f5.com/products/extensions/f5-telemetry-streaming/latest/) - for logging and reporting
        - [Cloud Failover Extension (CFE)](https://clouddocs.f5.com/products/extensions/f5-cloud-failover/latest/) - for updating ip and routes mappings
    - Additional cloud services like private endpoints can be used to address calls to native services traversing the Internet.
  - See [Security](#security) section for more details. 

- This solution template provides an **initial** deployment only for an "infrastructure" use case (meaning that it does not support managing the entire deployment exclusively via the template's "Redeploy" function). This solution leverages metadata to send the instance **startup script**, which is only used to provide an initial BIG-IP configuration and not as the primary configuration API for a long-running platform. Although "Redeploy" can be used to update some cloud resources, as the BIG-IP configuration needs to align with the cloud resources, like IPs to NICs, updating one without the other can result in inconsistent states, while updating other resources, like the **image** or **instanceType**, can trigger an entire instance re-deloyment. For instance, to upgrade software versions, traditional in-place upgrades should be leveraged. See [AskF5 Knowledge Base](https://support.f5.com/csp/article/K84554955) and [Changing the BIG-IP Deployment](#changing-the-big-ip-deployment) for more information.

- If you have cloned this repository to modify the templates or BIG-IP config files and published to your own location, you can use the **imports** section of the configuration template file to specify the new location of the customized templates and the **bigIpRuntimeInitConfig** input parameter to specify the new location of the BIG-IP Runtime-Init config. See main [/examples/README.md](#cloud-configuration) for more template customization details. See [Changing the BIG-IP Deployment](#changing-the-big-ip-deployment) for more BIG-IP customization details.

- In this solution, the BIG-IP VE has the [LTM](https://f5.com/products/big-ip/local-traffic-manager-ltm) and [ASM](https://f5.com/products/big-ip/application-security-manager-asm) modules enabled to provide advanced traffic management and web application security functionality. 

- If you would like to view all available images, run the following command from the **gcloud** command line: ```$ gcloud compute images list --project f5-7626-networks-public | grep f5```

- This directory contains a schema file which helps manage the required fields and set defaults to optional fields.  For example, if you omit the property for bigIpRuntimeInitPackageUrl in your configuration file,  we set the default URL to the latest available version.

- **Important**: For multi-NIC deployments, this solution configures the second interface of the instance as the MGMT interface.  This allows the first interface to be used by Google Cloud resources such as forwarding rules and load balancers for application traffic.  To connect to the MGMT interface (nic1) get the IP address from the instance properties and use your management tool of choice.  Note: The Google Cloud console and gcloud SSH connection options target nic0 and will not connect to the instance correctly.

- This template can send non-identifiable statistical information to F5 Networks to help us improve our templates. You can disable this functionality by setting the **autoPhonehome** system class property value to false in the F5 Declarative Onboarding declaration. See [Sending statistical information to F5](#sending-statistical-information-to-f5).

- See [trouble shooting steps](#troubleshooting-steps) for more details.

### Template Input Parameters

| Parameter | Required | Description |
| --- | --- | --- |
| appContainerName | No | The name of a container to download and install which is used for the example application server(s). If this value is left blank, the application module template is not deployed. |
| bigIpImage | No | Name of BIG-IP custom image found in the Google Cloud Marketplace. Example value: `f5-bigip-16-0-1-1-0-0-6-payg-best-200mbps-210129040615`. You can find the names of F5 marketplace images in the README for this template or by running the command: `gcloud compute images list --filter="name~f5"`. |
| bigIpInstanceType | No | Instance type assigned to the application, for example 'n1-standard-1'. |
| bigIpRuntimeInitConfig | No | Supply a URL to the bigip-runtime-init configuration file in YAML or JSON format, or an escaped JSON string to use for f5-bigip-runtime-init configuration. |
| bigIpRuntimeInitPackageUrl | No | Supply a URL to the bigip-runtime-init package. |
| numNics | No | Enter valid number of network interfaces (1-3) to create on the BIG-IP VE instance. |
| restrictedSrcAddressMgmt | Yes | This field restricts management access to specific networks or addresses. Enter an IP address or address range in CIDR notation separated by a space.  **IMPORTANT** This solution requires your Management's subnet at a minimum in order for the peers to cluster.  For example, '10.0.11.0/24 55.55.55.55/32' where 10.0.11.0/24 is your local management subnet and 55.55.55.55/32 is a specific address (ex. orchestration host/desktop/etc.). |
| restrictedSrcAddressApp | Yes | This field restricts web application access to a specific network or address; the port is defined using applicationPort parameter. Enter an IP address or address range in CIDR notation separated by a space. |
| restrictedSrcAddressAppInternal | Yes | This field restricts web application access to a specific private network or address. Enter an IP address or address range in CIDR notation separated by a space. |
| tagValues | No | Default key/value resource tags will be added to the resources in this deployment, if you would like the values to be unique adjust them as needed for each key. |
| uniqueString | Yes | A prefix that will be used to name template resources. Because some resources require globally unique names, we recommend using a unique value. |


### Template Outputs

| Name | Description | Required Resource | Type |
| --- | --- | --- | --- |
| appPrivateIp | Application Private IP Address | Application Template | string |
| appUsername | Application user name | Application Template | string |
| appVmName | Application Virtual Machine name | Application Template | string |
| bigIpManagementPrivateIp | Management Private IP Address | BIG-IP Template | string |
| bigIpManagementPrivateUrl | Management Private IP Address | BIG-IP Template | string |
| bigIpManagementPublicIpId | Management Public IP Address | Dag Template | string |
| bigIpManagementPublicUrl | Management Public IP Address | Dag Template | string |
| bigIpUsername | BIG-IP user name | BIG-IP Template | string |
| bigIpVmId | Virtual Machine resource ID | BIG-IP Template | string |
| vip1PrivateIp | Service (VIP) Private IP Address | Application Template | string |
| vip1PrivateUrlHttp | Service (VIP) Private HTTP URL | Application Template | string |
| vip1PrivateUrlHttps | Service (VIP) Private HTTPS URL | Application Template | string |
| vip1PublicIp | Service (VIP) Public IP Address | Dag Template | string |
| vip1PublicIpDns | Service (VIP) Public DNS | Dag Template | string |
| vip1PublicUrlHttp | Service (VIP) Public HTTP URL | Dag Template | string |
| vip1PublicUrlHttps | Service (VIP) Public HTTPS URL | Dag Template | string |
| networkId | Network self link | Network Template | string |
| wafPublicIps | External Public IP Addresses | Dag Template | array |


## Deploying this Solution

See [Prerequisites](#prerequisites).

To deploy this solution, you must use the [gcloud CLI](#deploying-via-the-gcloud-cli)

### Deploying via the gcloud CLI

To deploy the BIG-IP VE from the parent template YAML file, use the following command syntax:

```gcloud deployment-manager deployments create <your-deployment-name> --config <your-file-name.yaml> --description "<deployment-description>"```

Keep in mind the following:

- Follow the sample_quickstart.yaml file for guidance on what to include in the yaml file, include required imports and parameters
- *your-deployment-name*<br>This name must be unique.<br>
- *your-file-name.yaml*<br>If your file is not in the same directory as the Google SDK, include the full file path in the command.


### Changing the BIG-IP Deployment

You will most likely want or need to change the BIG-IP configuration. This generally involves referencing or customizing a [F5 BIG-IP Runtime Init](https://github.com/F5Networks/f5-bigip-runtime-init) configuration file and passing it through the **bigIpRuntimeInitConfig** template parameter as a URL or inline json. 

Example from sample_quickstart.json
```yaml
    bigIpRuntimeInitConfig: https://raw.githubusercontent.com/F5Networks/f5-google-gdm-templates-v2/v1.3.1.0/examples/autoscale/bigip-configurations/runtime-init-conf-payg.yaml
    cooldownPeriodSec: 60
```

**IMPORTANT**: Note the "raw.githubusercontent.com". Any URLs pointing to github **must** use the raw file format. 

The F5 BIG-IP Runtime Init configuration file can also be formatted in json and/or passed directly inline:

Example:
```yaml
    bigIpRuntimeInitConfig: "{\"controls\":{\"logLevel\":\"silly\"},\"pre_onboard_enabled\":[],\"runtime_parameters\":[{\"name\":\"ADMIN_PASS\",\"type\":\"static\",\"value\":\"ComplexPassword10+\"},{\"name\":\"ROOT_PASS\",\"type\":\"static\",\"value\":\"RootComplexPass20$\"},{\"name\":\"HOST_NAME\",\"type\":\"metadata\",\"metadataProvider\":{\"environment\":\"gcp\",\"type\":\"compute\",\"field\":\"name\"}},{\"name\":\"SELF_IP_INTERNAL\",\"type\":\"metadata\",\"metadataProvider\":{\"environment\":\"gcp\",\"type\":\"network\",\"field\":\"ip\",\"index\":2}},{\"name\":\"SELF_IP_EXTERNAL\",\"type\":\"metadata\",\"metadataProvider\":{\"environment\":\"gcp\",\"type\":\"network\",\"field\":\"ip\",\"index\":0}},{\"name\":\"GATEWAY\",\"type\":\"metadata\",\"metadataProvider\":{\"environment\":\"gcp\",\"type\":\"network\",\"field\":\"ip\",\"index\":0,\"ipcalc\":\"first\"}}],\"bigip_ready_enabled\":[{\"name\":\"provision_modules\",\"type\":\"inline\",\"commands\":[\"tmsh modify sys provision asm level nominal\"]},{\"name\":\"provision_rest\",\"type\":\"inline\",\"commands\":[\"/usr/bin/setdb provision.extramb 500\",\"/usr/bin/setdb restjavad.useextramb true\"]},{\"name\":\"save_sys_config\",\"type\":\"inline\",\"commands\":[\"tmsh save sys config\"]}],\"post_onboard_enabled\":[],\"extension_packages\":{\"install_operations\":[{\"extensionType\":\"do\",\"extensionVersion\":\"1.22.0\"},{\"extensionType\":\"as3\",\"extensionVersion\":\"3.29.0\",\"verifyTls\":false,\"extensionUrl\":\"https://github.com/F5Networks/f5-appsvcs-extension/releases/download/v3.29.0/f5-appsvcs-3.29.0-3.noarch.rpm\",\"extensionHash\":\"bcbba79b42b700b8d2b46937b65e6d09b035515a7a7e40aaeebb360fcfe7aa66\"},{\"extensionType\":\"fast\",\"extensionVersion\":\"1.10.0\"}]},\"extension_services\":{\"service_operations\":[{\"extensionType\":\"do\",\"type\":\"url\",\"value\":\"https://raw.githubusercontent.com/F5Networks/f5-bigip-runtime-init/main/examples/declarations/do_w_admin.json\",\"verifyTls\":false},{\"extensionType\":\"as3\",\"type\":\"url\",\"value\":\"https://cdn.f5.com/product/cloudsolutions/templates/f5-google-gdm-templates-v2/examples/modules/bigip/autoscale_as3.json\"}]},\"post_hook\":[{\"name\":\"example_webhook\",\"type\":\"webhook\",\"url\":\"https://postman-echo.com/post\",\"properties\":{\"optionalKey1\":\"optional_value1\",\"optionalKey2\":\"optional_value2\"}}]}"
    cooldownPeriodSec: 60    
```

NOTE: If providing the json inline as a template parameter, you must escape all double quotes so it can be passed as a single parameter string.

*TIP: If you haven't forked/published your own repository or don't have an easy way to host your own config files, passing the config as inline json via the template input parameter might be the quickest / most accessible option to test out different BIG-IP configs using this repository.*

F5 has provided the following example configuration files in the `examples/quickstart/bigip-configurations` folder:

- These examples install Automation Tool Chain packages and create WAF-protected services for a PAYG licensed deployment.
  - `runtime-init-conf-1nic-payg.yaml`
  - `runtime-init-conf-2nic-payg.yaml`
  - `runtime-init-conf-3nic-payg.yaml`
- These examples install Automation Tool Chain packages and create WAF-protected services for a BYOL licensed deployment.
  - `runtime-init-conf-1nic-byol.yaml`
  - `runtime-init-conf-2nic-byol.yaml`
  - `runtime-init-conf-3nic-byol.yaml`
- `Rapid_Deployment_Policy_13_1.xml` - This ASM security policy is supported for BIG-IP 13.1 and later.

See [F5 BIG-IP Runtime Init](https://github.com/F5Networks/f5-bigip-runtime-init) for more examples.

By default, this solution deploys a 3NIC BIG-IP using the example `runtime-init-conf-3nic-payg.yaml`.

To deploy a **1NIC** instance:
  1. Update the **bigIpRuntimeInitConfig** input parameter to reference a corresponding `1nic` config file (for example, runtime-init-conf-1nic-payg.yaml).
  2. Update the **numNics** input parameter to **1**.

To deploy a **2NIC** instance:
  1. Update the **bigIpRuntimeInitConfig** input parameter to reference a corresponding `2nic` config file (for example, runtime-init-conf-2nic-payg.yaml).
  2. Update the **numNics** input parameter to **2**.

- When specifying values for the bigIpInstanceType and numNics parameters, ensure that the instance type you select is appropriate for the deployment scenario. See [Google Machine Families](https://cloud.google.com/compute/docs/machine-types) for more information.

However, most changes require modifying the configurations themselves. For example:

To deploy a **BYOL** instance:

  1. Edit/modify the Declarative Onboarding (DO) declaration in a corresponding `byol` runtime-init config file with the new `regKey` value. 

Example:
```yaml
  My_License:
    class: License
    licenseType: regKey
    regKey: AAAAA-BBBBB-CCCCC-DDDDD-EEEEEEE
```
  2. Publish/host the customized runtime-init config file at a location reachable by the BIG-IP at deploy time (for example: github, Google Storage, etc.)
  3. Update the **bigIpRuntimeInitConfig** input parameter to reference the new URL of the updated configuration.
  4. Update the **bigIpImage** input parameter to use `byol` image.
        Example:
        ```yaml 
          bigIpImage: f5-bigip-16-0-1-1-0-0-6-payg-best-200mbps-210129040615
        ```

In order deploy additional **virtual services**:

For illustration purposes, this solution pre-provisions IP addresses and the runtime-init configurations contain an AS3 declaration to create an example virtual service. However, in practice, cloud-init runs once and is typically used for initial provisioning, not as the primary configuration API for a long-running platform. More typically in an infrastructure use case, virtual services are not included in the initial cloud-init configuration are added post initial deployment which involves:
  1. *Cloud* - Provisioning additional IPs on the desired Network Interfaces. Examples:
      - [gcloud compute forwarding-rules create](https://cloud.google.com/sdk/gcloud/reference/compute/forwarding-rules/create)
  2. *BIG-IP* - Creating Virtual Services that match those additional Secondary IPs 
      - Updating the [AS3](https://clouddocs.f5.com/products/extensions/f5-appsvcs-extension/latest/userguide/composing-a-declaration.html) declaration with additional Virtual Services (see **virtualAddresses:**).


*NOTE: For cloud resources, templates can be customized to pre-provision and update additional resources (for example: various combinations of NICs, forwarding rules, IAM roles, etc.). Please see [Getting Help](#getting-help) for more information. For BIG-IP configurations, you can leverage any REST or Automation Tool Chain clients like [Ansible](https://ansible.github.io/workshops/exercises/ansible_f5/3.0-as3-intro/),[Terraform](https://registry.terraform.io/providers/F5Networks/bigip/latest/docs/resources/bigip_as3),etc.*


## Validation

This section describes how to validate the template deployment, test the WAF service, and troubleshoot common problems.

### Validating the Deployment

To view the status of the example and module template deployments, navigate to **Deployment Manager > *Deployments* > *Deployment Name***. You should see a series of deployments, including one each for the example template as well as the application, network, dag, and bigip templates. The deployment status for the parent template deployment should indicate that the template has been successfully deployed.

Expected Deploy time for entire stack =~ 8-10 minutes.

If any of the deployments are in a failed state, proceed to the [Troubleshooting Steps](#troubleshooting-steps) section below.

### Accessing the BIG-IP

From Parent Template Outputs:
  - **Console**:  Navigate to **Deployment Manager > Deployments > *DEPLOYMENT_NAME* > Overview > Layout > Resources > Outputs**.
  - **Google CLI**:
    ```bash
    gcloud deployment-manager manifests describe --deployment=${DEPLOYMENT_NAME} | yq .layout | yq .resources[0].outputs[]
    ```

- Obtain the IP address of the BIG-IP Management Port:
  - **Console**: Navigate to **Deployment Manager > Deployments > *DEPLOYMENT_NAME* > Overview > Layout > Resources > Outputs > *bigIpManagementPublicIp***.
  - **Google CLI**: 
    ``` bash 
    gcloud deployment-manager manifests describe --deployment=${DEPLOYMENT_NAME} | yq .layout | yq '.resources[0].outputs[] | select(.name | contains("bigIpManagementPublicIp")).finalValue'
    ```

- Obtain the vmId of the BIG-IP Virtual Machine *(will be used for password later)*:
  - **Console**: Navigate to **Deployment Manager > Deployments > *DEPLOYMENT_NAME* > Overview > Layout > Resources > Outputs > bigIpVmId**.
  - **Google CLI**: 
    ```bash
    gcloud deployment-manager manifests describe --deployment=${DEPLOYMENT_NAME} | yq .layout | yq '.resources[0].outputs[] | select(.name | contains("bigIpVmId")).finalValue'
    ```

#### SSH
  - **SSH key authentication**: 
      ```bash
      ssh admin@${IP_ADDRESS_FROM_OUTPUT} -i ${YOUR_PRIVATE_SSH_KEY}
      ```
  - **Password authentication**: 
      ```bash 
      ssh quickstart@${IP_ADDRESS_FROM_OUTPUT}
      ``` 
      at prompt, enter your **bigIpVmId** (see above to obtain from template "Outputs")


#### WebUI
- Obtain the URL address of the BIG-IP Management Port:
  - **Console**: Navigate to **Deployment Manager > Deployments > *DEPLOYMENT_NAME* > Overview > Layout > Resources > Outputs > bigIpMgmtPublicUrl**.
  - **Google CLI**: 
    ```bash
    gcloud deployment-manager manifests describe --deployment=${DEPLOYMENT_NAME} | yq .layout | yq '.resources[0].outputs[] | select(.name | contains("bigIpMgmtPublicUrl")).finalValue'
    ```

- Open a browser to the Management URL:
  - NOTE: By default, the BIG-IP's WebUI starts with a self-signed cert. Follow your browsers instructions for accepting self-signed certs (for example, if using Chrome, click inside the page and type this "thisisunsafe". If using Firefox, click "Advanced" button, Click "Accept Risk and Continue").
  - Provide 
    - username: quickstart
    - password: **bigIpVmId** (obtained from parent template "Outputs" above)


### Further Exploring

#### WebUI
 - Navigate to **Virtual Services > Partition**. Select **Partition = `Tenant_1`**
    - Navigate to **Local Traffic > Virtual Servers**. You should see two Virtual Services (one for HTTP and one for HTTPS). The should show up as Green. Click on them to look at the configuration *(declared in the AS3 declaration)*

#### SSH

  - From tmsh shell, type 'bash' to enter the bash shell
    - Examine BIG-IP configuration via [F5 Automation Toolchain](https://www.f5.com/pdf/products/automation-toolchain-overview.pdf) declarations:
    ```bash
    curl -u admin: http://localhost:8100/mgmt/shared/declarative-onboarding | jq .
    curl -u admin: http://localhost:8100/mgmt/shared/appsvcs/declare | jq .
    curl -u admin: http://localhost:8100/mgmt/shared/telemetry/declare | jq . 
    ```
  - Examine the Runtime-Init Config downloaded: 
    ```bash 
    cat /config/cloud/runtime-init.conf
    ```


### Testing the WAF Service

To test the WAF service, perform the following steps:
- Obtain the IP address of the WAF service:
  - **Console**: Navigate to **Deployment Manager > Deployments > *DEPLOYMENT_NAME* > Overview > Layout > Resources > Outputs  > vip1PublicIp**.
  - **Google CLI**: 
      ```bash
      gcloud deployment-manager manifests describe --deployment=${DEPLOYMENT_NAME} | yq .layout | yq '.resources[0].outputs[] | select(.name | contains("vip1PublicIp")).finalValue'
      ```
- Verify the application is responding:
  - Paste the IP address in a browser: ```https://${IP_ADDRESS_FROM_OUTPUT}```
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

## Customizing this Solution

## Deleting this Solution

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
  - ```cat /config/cloud/runtime-init.conf```
- Check the logs (in order of invocation):
  - cloud-agent logs:
    - */var/log/boot.log*
    - */var/log/cloud-init.log*
    - */var/log/cloud-init-output.log*
  - runtime-init Logs:
    - */var/log/cloud/startup-script.log*: This file contains events that happen prior to execution of f5-bigip-runtime-init. If the files required by the deployment fail to download, for example, you will see those events logged here.
    - */var/log/cloud/bigipRuntimeInit.log*: This file contains events logged by the f5-bigip-runtime-init onboarding utility. If the configuration is invalid causing onboarding to fail, you will see those events logged here. If deployment is successful, you will see an event with the body "All operations completed successfully".
  - Automation Tool Chain Logs:
    - */var/log/restnoded/restnoded.log*: This file contains events logged by the F5 Automation Toolchain components. If an Automation Toolchain declaration fails to deploy, you will see more details for those events logged here.
- *GENERAL LOG TIP*: Search most critical error level errors first (for example, egrep -i err /var/log/<Logname>).

If you are unable to login to the BIG-IP instance(s), you can navigate to **Resource Groups > *RESOURCE_GROUP* > Overview > *INSTANCE_NAME* > Support and Troubleshooting > Serial console** for additional information from Google.


## Security

This GDM template downloads helper code to configure the BIG-IP system:

- f5-bigip-runtime-init.gz.run: The self-extracting installer for the F5 BIG-IP Runtime Init RPM can be verified against a SHA256 checksum provided as a release asset on the F5 BIG-IP Runtime Init public GitHub repository, for example: https://github.com/F5Networks/f5-bigip-runtime-init/releases/download/1.2.1/f5-bigip-runtime-init-1.2.1-1.gz.run.sha256.
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

If you want to verify the integrity of the template itself, F5 provides checksums for all of our templates. For instructions and the checksums to compare against, see [checksums-for-f5-supported-cft-and-arm-templates-on-github](https://devcentral.f5.com/codeshare/checksums-for-f5-supported-cft-and-arm-templates-on-github-1014).

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

| Google BIG-IP Image Version | BIG-IP Version |
| --- | --- |
| 16.0.101000 | 16.0.1.1 Build 0.0.6 |
| 14.1.400000 | 14.1.4 Build 0.0.11 |


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