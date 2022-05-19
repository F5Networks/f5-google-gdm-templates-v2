# Deploying the BIG-IP VE in GCP - Example Autoscale BIG-IP WAF (LTM + ASM) - Managed Instance Group (Frontend via GLB) - PAYG Licensing

[![Releases](https://img.shields.io/github/release/F5Networks/f5-google-gdm-templates-v2.svg)](https://github.com/F5Networks/f5-google-gdm-templates-v2/releases)
[![Issues](https://img.shields.io/github/issues/F5Networks/f5-google-gdm-templates-v2.svg)](https://github.com/F5Networks/f5-google-gdm-templates-v2/issues)


## Contents

  - [Contents](#contents)
  - [Introduction](#introduction) 
  - [Diagram](#diagram)
  - [Prerequisites](#prerequisites)
  - [Important Configuration Notes](#important-configuration-notes)
    - [Template Input Parameters](#template-input-parameters)
    - [Template Outputs](#template-outputs)
    - [Existing Network Parameters](#existing-network-parameters)
  - [Deploying this Solution](#deploying-this-solution)
    - [Deploying via the gcloud CLI](#deploying-via-the-gcloud-cli)
    - [Changing the BIG-IP Deployment](#changing-the-big-ip-deployment)
  - [Validation](#validation)
    - [Validating the Deployment](#validating-the-deployment)
    - [Testing the WAF Service](#testing-the-waf-service)
    - [Viewing WAF Logs](#viewing-waf-logs)
    - [Accessing the BIG-IP](#accessing-the-big-ip)
    - [Viewing Autoscale events](#viewing-autoscale-events)
  - [Updating this Solution](#updating-this-solution)
    - [Updating the Configuration](#updating-the-configuration)
    - [Upgrading the BIG-IP VE Image](#upgrading-the-big-ip-ve-image)
    - [Lifecycle Troubleshooting](#lifecycle-troubleshooting)
  - [Deleting this Solution](#deleting-this-solution)
  - [Troubleshooting Steps](#troubleshooting-steps)
  - [Security](#security)
  - [BIG-IP versions](#big-ip-versions)
  - [Resource Creation Flow Chart](#resource-creation-flow-chart)
  - [Documentation](#documentation)
  - [Getting Help](#getting-help)
    - [Filing Issues](#filing-issues)


## Introduction

This solution uses a parent template to launch several linked child templates (modules) to create an example BIG-IP autoscale solution. The linked templates are located in the [`examples/modules`](https://github.com/F5Networks/f5-google-gdm-templates-v2/tree/main/examples/modules) directory in this repository. **F5 recommends cloning this repository and modifying these templates to fit your use case.** 

***Full Stack (autoscale.py)***<br>
Use the *autoscale.py* parent template to deploy an example full stack autoscale solution, complete with virtual network, bastion *(optional)*, dag/ingress, access, BIG-IP(s) and example web application.  

***Existing Network Stack (autoscale-existing-network.py)***<br>
Use the *autoscale-existing-network.py* parent template to deploy the autoscale solution into an existing infrastructure. This template expects the virtual networks, subnets, and bastion host(s) have already been deployed. The example web application is also not part of this parent template as it intended for an existing environment.

The modules below create the following resources:

- **Network**: This template creates Virtual Networks, Subnets, and Route Tables. *(Full stack only)*
- **Bastion**: This template creates a generic example bastion for use when connecting to the management interfaces of BIG-IPs. *(Full stack only)*
- **Application**: This template creates a generic example application for use when demonstrating live traffic through the BIG-IPs. *(Full stack only)*
- **Disaggregation** *(DAG/Ingress)*: This template creates resources required to get traffic to the BIG-IP, including Firewalls, Forwarding Rules, internal/external Load Balancers, and accompanying resources such as health probes.
- **Access**: This template creates a custom IAM role for the BIG-IP instances and other resources to gain access to Google Cloud services such as compute and storage.
- **BIG-IP**: This template creates compute instances with F5 BIG-IP Virtual Editions provisioned with Local Traffic Manager (LTM) and Application Security Manager (ASM). Traffic flows from the Google load balancer to the BIG-IP VE instances and then to the application servers. The BIG-IP VE(s) are configured in single-NIC mode. Auto scaling means that as certain thresholds are reached, the number of BIG-IP VE instances automatically increases or decreases accordingly. The BIG-IP module template can be deployed separately from the example template provided here into an "existing" stack.

This solution leverages traditional Autoscale configuration management practices where each instance is created with an identical configuration as defined in the model. The BIG-IP's configuration, now defined in a single convenient YAML or JSON [F5 BIG-IP Runtime Init](https://github.com/F5Networks/f5-bigip-runtime-init) configuration file, leverages [F5 Automation Tool Chain](https://www.f5.com/pdf/products/automation-toolchain-overview.pdf) declarations which are easier to author, validate and maintain as code. For instance, if you need to change the configuration on the BIG-IPs in the deployment, instead of updating the existing instances directly, you update the instance model by passing a new config file (which references the updated Automation Toolchain declarations) via template's bigIpRuntimeInitConfig input parameter. The model will be responsible for maintaining the configuration across the deployment, updating existing instances and deploying new instances with the latest configuration.


## Diagram

![Configuration Example](diagram.png)


## Prerequisites

  - This solution requires a Google Cloud account that can provision objects described in the solution using the gcloud CLI:
      ```bash
      gcloud deployment-manager deployments create ${DEPLOYMENT_NAME} --config ${CONFIG_FILE}
      ```
  - This solution requires an [SSH key](https://cloud.google.com/compute/docs/instances/adding-removing-ssh-keys) for access to the BIG-IP instances.
  - This solution requires you to accept any Google Cloud Marketplace "License/Terms and Conditions" for the images used in this solution.
    - By default, this solution uses [F5 Advanced WAF with LTM, IPI and TC (PAYG - 25Mbps)](https://console.cloud.google.com/marketplace/product/f5-7626-networks-public/f5-big-awf-plus-payg-25mbps)
  - This solution creates service accounts, custom IAM roles, and service account bindings. The Google APIs Service Agent service account must be granted the Role Administrator and Project IAM Admin roles before deployment can succeed. For more information about this account, see the Google-managed service account [documentation](https://cloud.google.com/iam/docs/maintain-custom-roles-deployment-manager)


## Important Configuration Notes

- By default, this solution does not create a custom BIG-IP WebUI user as instances are not intended to be managed directly. However, an SSH key is installed to provide CLI access for demonstration and debugging purposes. 
  - ***IMPORTANT:** Accessing or logging into the instances themselves is for demonstration and debugging purposes only. All configuration changes should be applied by updating the model via the template instead.*
  - See [Changing the BIG-IP Deployment](#changing-the-big-ip-deployment) for more details.

- This solution requires Internet access for: 
  - Downloading additional F5 software components used for onboarding and configuring the BIG-IP (via GitHub.com). *NOTE: access via web proxy is not currently supported. Other options include 1) hosting the file locally and modifying the runtime-init package url and configuration files to point to local URLs instead or 2) baking them into a custom image (BYOL images only), using the [F5 Image Generation Tool](https://clouddocs.f5.com/cloud/public/v1/ve-image-gen_index.html).*
  - Contacting native cloud services for various cloud integrations: 
    - *Onboarding*:
        - [F5 BIG-IP Runtime Init](https://github.com/F5Networks/f5-bigip-runtime-init) - to fetch secrets from native vault services
    - *Operation*:
        - [F5 Application Services 3](https://clouddocs.f5.com/products/extensions/f5-appsvcs-extension/latest/) - for features like Service Discovery
        - [F5 Telemetry Streaming](https://clouddocs.f5.com/products/extensions/f5-telemetry-streaming/latest/) - for logging and reporting
  - See [Security](#security) section for more details. 

- F5 GDM templates do not reconfigure existing Google Cloud resources, such as firewall rules. Depending on your configuration, you may need to configure these resources to allow the BIG-IP VE(s) to receive traffic for your application. Similarly, the DAG example template that sets up the load balancer services configures forwarding rules and health checks on those resources to forward external traffic to the BIG-IP(s) on standard ports 443 and 80. F5 recommends cloning this repository and modifying the module templates to fit your use case.

- If you have cloned this repository to modify the templates or BIG-IP config files and published to your own location, you can use the **templateBaseUrl** and **artifactLocation** input parameters to specify the new location of the customized templates and the **bigIpRuntimeInitConfig** input parameter to specify the new location of the BIG-IP Runtime-Init config. See main [/examples/README.md](../../README.md#cloud-configuration) for more template customization details. See [Changing the BIG-IP Deployment](#changing-the-big-ip-deployment) for more BIG-IP customization details.

- In this solution, the BIG-IP VE has the [LTM](https://f5.com/products/big-ip/local-traffic-manager-ltm) and [ASM](https://f5.com/products/big-ip/application-security-manager-asm) modules enabled to provide advanced traffic management and web application security functionality. 

- You are required to specify which Availability Zone you are deploying the application in. See [Google Cloud Availability Zones](https://cloud.google.com/compute/docs/regions-zones) for a list of regions and their corresponding availability zones.

- See [trouble shooting steps](#troubleshooting-steps) for more details.


### Template Input Parameters

These are specified in the configuration file. See sample_autoscale.yaml

**Required** means user input is required because there is no default value or an empty string is not allowed. If no value is provided, the template will fail to launch. In some cases, the default value may only work on the first deployment due to creating a resource in a global namespace and customization is recommended. See the Description for more details.
Note: These are specified in the configuration file. See sample_autoscale.yaml

| Parameter | Required | Default | Type | Description |
| --- | --- | --- | --- | --- |
| appContainerName | No | 'f5devcentral/f5-demo-app:latest' | string | The name of a container to download and install which is used for the example application server. If this value is left blank, the application module template is not deployed. |
| application | No | f5app | string | Application label. |
| bigIpCoolDownPeriodSec | No | 60 | integer | Number of seconds Google Autoscaler waits to start checking BIG-IP instances on first boot. |
| bigIpImageName | No | f5-bigip-16-1-2-2-0-0-28-payg-best-25mbps-220505074742 | string | Name of BIG-IP custom image found in the Google Cloud Marketplace. Example value: `f5-bigip-16-1-2-2-0-0-28-payg-best-25mbps-220505074742`. You can find the names of F5 marketplace images in the README for this template or by running the command: `gcloud compute images list --project f5-7626-networks-public --filter="name~f5"`. |
| bigIpInstanceTemplateVersion | No | 1 | integer | Version of the instance template to create. When updating deployment properties of the BIG-IP instances, you must provide a unique value for this parameter. |
| bigIpInstanceType | No | n1-standard-4 | string | Instance type assigned to the application, for example 'n1-standard-4'. |
| bigIpRuntimeInitConfig | No | https://raw.githubusercontent.com/F5Networks/f5-google-gdm-templates-v2/v2.2.0.0/examples/autoscale/bigip-configurations/runtime-init-conf-payg-with-app.yaml | string | Supply a URL to the bigip-runtime-init configuration file in YAML or JSON format. |
| bigIpRuntimeInitPackageUrl | No | https://cdn.f5.com/product/cloudsolutions/f5-bigip-runtime-init/v1.4.1/dist/f5-bigip-runtime-init-1.4.1-1.gz.run | string | Supply a URL to the bigip-runtime-init package. |
| bigIpScaleOutCpuThreshold | No | 0.8 | integer | High CPU Percentage threshold to begin scaling out BIG-IP VE instances. |
| bigIpScalingMaxSize | No | 8 | integer | Maximum number of BIG-IP instances that can be created in the Auto Scale Group. |
| bigIpScalingMinSize | No | 1 | integer | Minimum number of BIG-IP instances you want available in the Auto Scale Group. |
| cost | No | f5cost | string | Cost Center label. |
| environment | No | f5env | string | Environment label. |
| group | No | f5group | string | Group Tag. |
| owner | No | f5owner | string | Owner label. |
| provisionPublicIp | No | true | boolean | Provision Public IP addresses for the BIG-IP Management interface. By default, this is set to true. If set to false, the solution will deploy a bastion host instead in order to provide access.  |
| region | No | us-west1 | string | Google Cloud region used for this deployment, for example 'us-west1'. |
| restrictedSrcAddressApp | Yes |  | array | An IP address range (CIDR) that can be used to restrict access web traffic (80/443) to the BIG-IP instances, for example 'X.X.X.X/32' for a host, '0.0.0.0/0' for the Internet, etc. **NOTE**: The VPC CIDR is automatically added for internal use. |
| restrictedSrcAddressMgmt | Yes |  | array | An IP address range (CIDR) used to restrict SSH and management GUI access to the BIG-IP Management or bastion host instances. Provide a YAML list of addresses or networks in CIDR notation, for example, '- 55.55.55.55/32' for a host, '- 10.0.0.0/8' for a network, etc. NOTE: If using a Bastion Host (when ProvisionPublicIp = false), you must also include the Bastion's source network, for example '- 10.0.0.0/8'. **IMPORTANT**: The VPC CIDR is automatically added for internal use (access via bastion host, clustering, etc.). Please restrict the IP address range to your client, for example '- X.X.X.X/32'. Production should never expose the BIG-IP Management interface to the Internet. |
| uniqueString | No | myuniqstr | string | A prefix that will be used to name template resources. Because some resources require globally unique names, we recommend using a unique value. |
| update | No | false | boolean | This specifies when to add dependency statements to the autoscale related resources. By default, this is set to false. Specify false when first deploying and right before deleting. Specify True when updating the deployment. See [updating this solution](#updating-this-solution) section below.|
| zone | No | us-west1-a | string | Enter the availability zone where you want to deploy the application, for example 'us-west1-a'. |


#### Existing Network Parameters

| Parameter | Required | Default | Type | Description |
| --- | --- | --- | --- | --- |
| subnets | Yes | | object | Subnet object which provides names for mgmt and app subnets |
| subnets.mgmtSubnetName | Yes | | string | Management subnet name | 
| subnets.appSubnetName | Yes | | string | Application subnet name |
| networkName | Yes | bigip-network | string | Network name |


### Template Outputs

| Name | Required Resource | Type | Description | 
| --- | --- | --- | --- |
| appInstanceGroupName |  | string | Application instance group name. |
| appInstanceGroupSelfLink |  | string | Application instance group self link. |
| bastionInstanceGroupName |  | string | Bastion instance group name. |
| bastionInstanceGroupSelfLink |  | string | Bastion instance group self link. |
| bigIpInstanceGroupName |  | string | BIG-IP instance group name. |
| bigIpInstanceGroupSelfLink |  | string | BIG-IP instance group self link. |
| deploymentName |  | string | Autoscale WAF deployment name. |
| networkName |  | string | Network name. |
| networkSelfLink |  | string | Network self link. |
| wafExternalHttpsUrl |  | string | WAF external HTTP URL. |
| wafInternalHttpsUrl |  | string | WAF external HTTPS URL. |
| wafPublicIp |  | string | WAF public IP. |


## Deploying this Solution

See [Prerequisites](#prerequisites).

To deploy this solution, you must use the [gcloud CLI](#deploying-via-the-gcloud-cli)


### Deploying via the gcloud CLI

To deploy the BIG-IP VE from the parent template YAML file, use the following command syntax:

```bash
gcloud deployment-manager deployments create ${DEPLOYMENT_NAME} --config ${CONFIG_FILE}```
```

Keep in mind the following:

- Follow the sample_autoscale.yaml file for guidance on what to include in the yaml *CONFIG_FILE*, include required imports and parameters
- *DEPLOYMENT_NAME*<br>This name must be unique.<br>
- *CONFIG_FILE*<br>If your file is not in the same directory as the Google SDK, include the full file path in the command.

### Changing the BIG-IP Deployment

You will most likely want or need to change the BIG-IP configuration. This generally involves referencing or customizing a [F5 BIG-IP Runtime Init](https://github.com/F5Networks/f5-bigip-runtime-init) configuration file and passing it through the **bigIpRuntimeInitConfig** parameter as a URL. 

Example from sample_autoscale.yaml
```yaml
    ### (OPTIONAL) Supply a URL to the bigip-runtime-init configuration file in YAML or JSON format
    bigIpRuntimeInitConfig: https://raw.githubusercontent.com/F5Networks/f5-google-gdm-templates-v2/v2.2.0.0//examples/autoscale/bigip-configurations/runtime-init-conf-payg.yaml
```

***IMPORTANT**: Note the "raw.githubusercontent.com". Any URLs pointing to GitHub **must** use the raw file format.*

F5 has provided the following example configuration files in the `examples/autoscale/bigip-configurations` folder:

- `runtime-init-conf-bigiq.yaml` - This configuration file installs packages and creates WAF-protected services for a BIG-IQ licensed deployment based on the Automation Toolchain declaration URLs listed above.
- `runtime-init-conf-payg.yaml` - This inline configuration file installs packages and creates WAF-protected services for a PAYG licensed deployment.
- `Rapid_Deployment_Policy_13_1.xml` - This ASM security policy is supported for BIG-IP 13.1 and later.

See [F5 BIG-IP Runtime Init](https://github.com/F5Networks/f5-bigip-runtime-init) for more examples. 
 
By default, this solution deploys the `runtime-init-conf-payg.yaml` configuration. 

This example configuration does not require any modifications to deploy successfully *(Disclaimer: "Successfully" implies the template deploys without errors and deploys BIG-IP WAFs capable of passing traffic. To be fully functional as designed, you would need to have satisfied the [Prerequisites](#prerequisites))*. However, in production, these files would commonly be customized. Some examples of small customizations or modifications are provided below. 

The example AS3 declaration in this config uses [Service Discovery](https://clouddocs.f5.com/products/extensions/f5-appsvcs-extension/latest/userguide/service-discovery.html#using-service-discovery-with-as3) to populate the pool with the private IP addresses of application servers in a instance group. By default, the fields for the service discovery configuration are rendered similarly from Google Cloud metadata. If the application instance group requires different values or configuration, you would need to customize them in the runtime-init config being downloaded. 

To change the Pool configuration:

  1. Edit/modify the AS3 Declaration (AS3) declaration in a corresponding runtime-init config file with the new `Pool` values. 

Example:
```yaml
           Shared_Pool:
              class: Pool
              remark: Service 1 shared pool
              members:
                - addressDiscovery: gce
                  addressRealm: private
                  tagKey: <YOUR_TAG_KEY>
                  tagValue: <YOUR_TAG_VALUE>
                  region: '{{{REGION}}}'
                  servicePort: 80
                  updateInterval: 60
              monitors:
                - http
```

  - *NOTE:* 
    - The managed identity assigned to the BIG-IP VE instance(s) must have read permissions on the managed instance group resource.
    - The Service Discovery configuration listed above targets a specific managed instance group ID to reduce the number of requests made to the Google Cloud API endpoints. When choosing capacity for the BIG-IP VE and application instance group, it is possible to exceed the API request limits. Consult the Google Compute Engine API rate limits [documentation](https://cloud.google.com/compute/docs/api-rate-limits) for more information.

  - You can also use another pool configuration entirely. For example, using the [FQDN](https://clouddocs.f5.com/products/extensions/f5-appsvcs-extension/latest/declarations/discovery.html#using-an-fqdn-pool-to-identify-pool-members) Service Discovery instead to point to a DNS name.

```yaml
              class: Pool
              remark: Service 1 shared pool
              members:
              - addressDiscovery: fqdn
                autoPopulate: true
                hostname: <WWW.YOURSITE.COM>
                servicePort: 80
```

  2. Publish/host the customized runtime-init config file at a location reachable by the BIG-IP at deploy time (for example, GitHub, Google Cloud Storage, etc.).
  3. Update the **bigIpRuntimeInitConfig** input parameter to reference the new URL of the updated configuration.
  4. Deploy or Re-Deploy.


## Validation

This section describes how to validate the template deployment, test the WAF service, and troubleshoot common problems.


### Validating the Deployment

To view the status of the example and module template deployments, navigate to **Deployment Manager > Deployments > Deployment Name**. You should see a series of deployments, including one each for the example template as well as the access, application, network, dag, and bigip templates. The deployment status for the parent template deployment should indicate that the template has been successfully deployed.

Expected Deploy time for entire stack =~ 8-10 minutes.

If any of the deployments are in a failed state, proceed to the [Troubleshooting Steps](#troubleshooting-steps) section below.

### Testing the WAF Service

To test the WAF service, perform the following steps:
- Check the instance group health state; instance health is based on Google Cloud's ability to connect to your application via the instance group's load balancer. The health state for each instance should be "Healthy". If the state is "Unhealthy", proceed to the [Troubleshooting Steps](#troubleshooting-steps) section.
- Obtain the IP address of the WAF service:
  - **Console**: Navigate to **Deployment Manager > Deployments > *DEPLOYMENT_NAME* > Overview > Layout > Resources > Outputs  > wafPublicIp**.
  - **gcloud CLI**: 
      ```bash
      gcloud deployment-manager manifests describe --deployment=${DEPLOYMENT_NAME} --format="value(layout)" | yq '.resources[0].outputs[] | select(.name | contains("wafPublicIp")).finalValue'
      ```
- Verify the application is responding:
  - Paste the IP address in a browser: ```https://${IP_ADDRESS_FROM_OUTPUT}```
      - ***NOTE**: By default, the Virtual Service starts with a self-signed cert. Follow your browser's instructions for accepting self-signed certs (for example, if using Chrome, click inside the page and type this "thisisunsafe". If using Firefox, click "Advanced" button, Click "Accept Risk and Continue", etc.).*
  - Use curl: 
      ```shell
       curl -sko /dev/null -w '%{response_code}\n' https://${IP_ADDRESS_FROM_OUTPUT}
       ```
- Verify the WAF is configured to block illegal requests:
    ```shell
    curl -sk -X DELETE https://${IP_ADDRESS_FROM_OUTPUT}
    ```
  The response should include a message that the request was blocked, and a reference support ID
    Example:
    ```shell
    $ curl -sko /dev/null -w '%{response_code}\n' https://55.55.55.55
    200
    $ curl -sk -X DELETE https://55.55.55.55
    <html><head><title>Request Rejected</title></head><body>The requested URL was rejected. Please consult with your administrator.<br><br>Your support ID is: 2394594827598561347<br><br><a href='javascript:history.back();'>[Go Back]</a></body></html>
    ```

### Viewing WAF Logs

- This solution utilizes [F5 Telemetry Streaming extension](https://clouddocs.f5.com/products/extensions/f5-telemetry-streaming/latest/) which sends WAF logs to the Google Cloud Logging service.
- You can view the WAF logs by going to the [Google Cloud Logging Console](https://console.cloud.google.com/logs) and querying for the value used for logId in the F5 BIG-IP Runtime Init My_Remote_Logs_Namespace configuration. The default value is ***f5-waf-logs***.

### Accessing the BIG-IP

- NOTE:
  - The following CLI commands require the gcloud CLI and yq: https://github.com/mikefarah/yq#install
  - When **false** is selected for **provisionPublicIp**, you must connect to the BIG-IP instance via a bastion host. Once connected to a bastion host, you may then connect via SSH to the private IP addresses of the BIG-IP instances in *uniqueString*-bigip-igm.

From Parent Template Outputs:
  - **Console**:  Navigate to **Deployment Manager > Deployments > *DEPLOYMENT_NAME* > Overview > Layout > Resources > Outputs**.
  - **Google CLI**:
    ```bash
    gcloud deployment-manager manifests describe --deployment=${DEPLOYMENT_NAME} --format="value(layout)" | yq .resources[0].outputs
    ```

- Obtain the IP address of the BIG-IP Management Port:
  - **gcloud CLI**:

      - Instance Group (BIG-IP)
        - **Console**: Navigate to **Deployment Manager > Deployments > *DEPLOYMENT_NAME* > Overview > Layout > Resources > Outputs > *bigIpInstanceGroupName***.
        - **Google CLI**: 
          ``` bash 
          BIG_IP_INSTANCE_GROUP_NAME=$(gcloud deployment-manager manifests describe --deployment=${DEPLOYMENT_NAME} --format="value(layout)" | yq '.resources[0].outputs[] | select(.name | contains("bigIpInstanceGroupName")).finalValue')
          ```
      - Instances (BIG-IP)
        ```
        ZONE="us-west1-a"
        gcloud compute instance-groups list-instances ${BIG_IP_INSTANCE_GROUP_NAME} --zone=${ZONE} --format json | jq -r .[].instance
        ```

    - Instance Group (Bastion)
        - **Console**: Navigate to **Deployment Manager > Deployments > *DEPLOYMENT_NAME* > Overview > Layout > Resources > Outputs > *bastionInstanceGroupName***.
        - **Google CLI**: 
          ``` bash 
          BASTION_INSTANCE_GROUP_NAME=$(gcloud deployment-manager manifests describe --deployment=${DEPLOYMENT_NAME} --format="value(layout)" | yq '.resources[0].outputs[] | select(.name | contains("bastionInstanceGroupName")).finalValue')
          ```
    - Instances (Bastion)
        ```
        gcloud compute instance-groups list-instances ${BASTION_INSTANCE_GROUP_NAME} --zone=${ZONE} --format json | jq -r .[].instance
        ```
 
    - Public IPs (BIG-IP or Bastion instance): 
      ```shell 
      INSTANCE="An instance name or URL from output above"
      gcloud compute instances describe ${INSTANCE} --zone=${ZONE} --format='value(networkInterfaces.accessConfigs[0].natIP)'
      ```

    - Private IPs (BIG-IP): 
      ```shell
      gcloud compute instances describe ${INSTANCE} --zone=${ZONE} --format='value(networkInterfaces.networkIP)'
      ```

- Login in via SSH:
  - **SSH key authentication**: 
    ```bash
    ssh admin@${IP_ADDRESS_FROM_OUTPUT} -i ${YOUR_PRIVATE_SSH_KEY}
    ```

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

- Login in via WebUI:
  - As mentioned above, no password is configured by default. If you would like or need to login to the GUI for debugging or inspection, you can create a custom username/password by logging in to admin account via SSH (per above) and use tmsh to create one:
    At the TMSH prompt ```admin@(bigip1))(cfg-sync Standalone)(Active)(/Common)(tmos)#```:
      ```shell
      create auth user <YOUR_WEBUI_USERNAME> password <YOUR_STRONG_PASSWORD> partition-access add { all-partitions { role admin } }

      save sys config
      ```

  - Open a browser to the Management IP
    - ```https://${IP_ADDRESS_FROM_OUTPUT}:8443```

        

    - OR when you are going through a bastion host (when **provisionPublicIP** = **false**):

        From your desktop client/shell, create an SSH tunnel:
        ```bash
        ssh -i [PROJECT_USER_PRIVATE_KEY] [PROJECT_USER]@[BASTION-HOST-PUBLIC-IP] -L 8443:[BIG-IP-MGMT-PRIVATE-IP]:[BIGIP-GUI-PORT]
        ```
        For example:
        ```bash
        ssh -i ~/.ssh/mykey.pem myprojectuser@34.82.102.190 -L 8443:10.0.0.2:8443
        ```

        You should now be able to open a browser to the BIG-IP UI from your desktop:

        https://localhost:8443


  - NOTE: 
    - By default, for Single NIC deployments, the management port is 8443.
    - By default, the BIG-IP's WebUI starts with a self-signed cert. Follow your browsers instructions for accepting self-signed certs (for example, if using Chrome, click inside the page and type this "thisisunsafe". If using Firefox, click "Advanced" button, Click "Accept Risk and Continue" ).

  - To Login: 
    - username: `<YOUR_WEBUI_USERNAME>`
    - password: `<YOUR_STRONG_PASSWORD>`

### Viewing Autoscale events

- This solution utilizes [F5 Telemetry Streaming extension](https://clouddocs.f5.com/products/extensions/f5-telemetry-streaming/latest/) which sends metrics to Google Cloud Monitoring service and those metrics are used by autoscaling policies to perform autoscale events.
- Autoscaling events can be seen under the instance group monitoring view. 

      
### Further Exploring

#### Using the WebUI
 - Navigate to **Local Traffic > Virtual Servers**. In the upper right corner, select **Partition = `Tenant_1`**.
 - You should now see two Virtual Services (one for HTTP and one for HTTPS). They should show up as Green. Click on them to look at the configuration *(declared in the AS3 declaration)*

#### Using SSH

  - From tmsh shell, type 'bash' to enter the bash shell.
    
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


## Updating this Solution

### BIG-IP Lifecycle Management

As mentioned in the [Introduction](#introduction), if you need to change the configuration on the BIG-IPs in the deployment, instead of updating the existing instances directly, you update the instance model by passing a new config file (which references the updated Automation Toolchain declarations) via the template's bigIpRuntimeInitConfig input parameter. The model will be responsible for maintaining the configuration across the deployment, updating existing instances and deploying new instances with the latest configuration.

This happens by leveraging Google Cloud's Managed Instance Group's [automatic rolling out](https://cloud.google.com/compute/docs/instance-groups/rolling-out-updates-to-managed-instance-groups) feature.

By default, Rolling Upgrades are configured to upgrade in batches of 20% with zero pause time in between sets and minimum of 20% of healthy nodes available. To modify, you can customize the `/module/bigip-autoscale` template.

#### Updating the Configuration

1. Modify the **bigIpRuntimeInitConfig** parameter value to reference a new URL to trigger a model update. Example:
  - If using tags for versions, change from `v1.2.0.0`
    ```yaml
        "bigIpRuntimeInitConfig": "https://raw.githubusercontent.com/F5Networks/f5-google-gdm-templates-v2/v1.2.0.0/examples/autoscale/bigip-configurations/runtime-init-conf-payg.yaml"
    ```
    to `v1.3.1.0`
    ```yaml
        "bigIpRuntimeInitConfig": "https://raw.githubusercontent.com/F5Networks/f5-google-gdm-templates-v2/v1.3.1.0/examples/autoscale/bigip-configurations/runtime-init-conf-payg.yaml"

    ```
2. Modify the **update** parameter to True. This removes dependencies that are required for the initial deployment only.
3. Modify the **bigIpInstanceTemplateVersion** parameter to 2 (or a subsequent version number if you have redeployed multiple times). Specifying a unique value causes the deployment to create a new instance template for the VM instances.
4. Re-deploy the template with new **bigIpRuntimeInitConfig** parameter updated in your configuration file.
    ```bash
    gcloud deployment-manager deployments update ${DEPLOYMENT_NAME} --config ${CONFIG_FILE}
    ```  

#### Upgrading the BIG-IP VE Image
As new BIG-IP versions are released, existing Managed Instance Groups can be upgraded to use those new images with same procedure. 

1. Modify the **bigIpImageName** input parameter value to new BIG-IP version in your configuration file.

2. Re-deploy the template with new **bigIpImageName** parameter.
    ```bash 
    gcloud deployment-manager deployments update ${DEPLOYMENT_NAME} --config ${CONFIG_FILE}
    ```  

#### Lifecycle Troubleshooting

If a new configuration update fails (for example, invalid config, typo, etc.) and Rolling Upgrade fails to complete.

1. [Stop](https://cloud.google.com/sdk/gcloud/reference/deployment-manager/deployments/stop) any hung Deployments.
    - **gcloud CLI**: 
        ```bash 
        gcloud deployment-manager deployments stop ${DEPLOYMENT_NAME}
        ```
2. [Stop](https://cloud.google.com/deployment-manager/docs/deployments/updating-deployments#stop_an_update) any updates in progress.
    - **gcloud CLI**: 
      ```bash 
      gcloud deployment-manager deployments stop ${DEPLOYMENT_NAME}
      ```
3. Modify parameters to update the model.
    - Modify the parameter that resulted in failure (for example, a previous or working **bigIpRuntimeInitConfig** value or image).
    - Modify Scaling Size to deploy new instances.
      - Increase **minNumReplicas** parameter value by 1 or more.
4. Re-deploy the template with new parameter values (the failed parameter and **minNumReplicas**).
5. Confirm newly instantiated instance(s) are healthy.
6. [Delete](https://cloud.google.com/sdk/gcloud/reference/compute/instances/delete) failed instances.
    - **gcloud CLI**: 
      ```bash 
      gcloud compute instances delete ${INSTANCE_NAME} --zone=${ZONE}
      ```


## Deleting this Solution

### Deleting the deployment via Google Cloud Console 

1. Navigate to **Deployment Manager** > Select "Deployments" Icon.

2. Select your parent template deployment by clicking the check box next to the deployment name.

3. Click **Delete**.

4. Choose an option for retaining template resources.

5. Click **Delete All** to confirm.

### Deleting the deployment using the gcloud CLI

Before deleting this solution, if you had previously updated the deployment, you must first redeploy while specifying "false" for the update input parameter in your configuration file:

```bash
    gcloud deployment-manager deployments update ${DEPLOYMENT_NAME} --config ${UPDATED_CONFIG_FILE}
```

Do not change the bigIpInstanceTemplateVersion input parameter value when redeploying before delete.

After redeploying with update:false, you can delete the deployment without dependency errors:

```bash
  gcloud deployment-manager deployments delete ${DEPLOYMENT_NAME} -q
```


### Troubleshooting Steps

There are generally two classes of issues:

1. Template deployment itself failed
2. Resource(s) within the template failed to deploy

To verify that all templates deployed successfully, follow the instructions under **Validating the Deployment** above to locate the failed deployment(s).

Click on the name of a failed deployment and then click **Events**. Click the link in the red banner at the top of the deployment overview for details about the failure cause. 

If the template passed validation but individual template resources have failed to deploy, expand **Deployment Details**, then click on the Operation details column for the failed resource. ***Note:** When creating a GitHub issue for a template, please include as much information as possible from the failed Google Cloud deployment/resource events.*

Common deployment failure causes include:
- Required fields were left empty or contained incorrect values (input type mismatch, prohibited characters, malformed YAML, etc.) causing template validation failure.
- Insufficient permissions to create the deployment or resources created by a deployment.
- Resource limitations (exceeded limit of IP addresses or compute resources, etc.).
- Google Cloud service issues (these will usually surface as 503 internal server errors in the deployment status error message).

If all deployments completed "successfully" but the BIG-IP or Service is not reachable, then log in to the BIG-IP instance via SSH to confirm the BIG-IP deployment was successful (for example, if startup scripts completed as expected on the BIG-IP). To verify BIG-IP deployment, perform the following steps:
- Obtain the IP address of the BIG-IP instance. See instructions [above](#accessing-the-bigip-ip).
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
- *GENERAL LOG TIP*: Search most critical error level errors first (for example, `egrep -i err /var/log/<Logname>`).


## Security

This GDM template downloads helper code to configure the BIG-IP system:

- **f5-bigip-runtime-init.gz.run**: The self-extracting installer for the F5 BIG-IP Runtime Init RPM can be verified against a SHA256 checksum provided as a release asset on the F5 BIG-IP Runtime Init public GitHub repository. For example: https://github.com/F5Networks/f5-bigip-runtime-init/releases/download/1.2.1/f5-bigip-runtime-init-1.2.1-1.gz.run.sha256.
- **F5 BIG-IP Runtime Init**: The self-extracting installer script extracts, verifies, and installs the F5 BIG-IP Runtime Init RPM package. Package files are signed by F5 and automatically verified using GPG.
- **F5 Automation Toolchain components**: F5 BIG-IP Runtime Init downloads, installs, and configures the F5 Automation Toolchain components. Although it is optional, F5 recommends adding the extensionHash field to each extension install operation in the configuration file. The presence of this field triggers verification of the downloaded component package checksum against the provided value. The checksum values are published as release assets on each extension's public GitHub repository. For example: https://github.com/F5Networks/f5-appsvcs-extension/releases/download/v3.18.0/f5-appsvcs-3.18.0-4.noarch.rpm.sha256

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

If you want to verify the integrity of the template itself, F5 provides checksums for all of our templates. For instructions and the checksums to compare against, see [this article](https://community.f5.com/t5/crowdsrc/checksums-for-f5-supported-cloud-templates-on-github/ta-p/284471) about Checksums for F5 Supported Cloud templates on GitHub.

List of endpoints BIG-IP may contact during onboarding:
- BIG-IP image default:
    - vector2.brightcloud.com (by BIG-IP image for [IPI subscription validation](https://support.f5.com/csp/article/K03011490))
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

| Google Cloud BIG-IP Image Version | BIG-IP Version |
| --- | --- |
| 16.1.200000 | 16.1.2.1 Build 0.0.10 |
| 14.1.400000 | 14.1.4.4 Build 0.0.4* |

***Note**: Due to an issue with the default ca-bundle, you may not host F5 BIG-IP Runtime Init configuration files in a Google Storage bucket when deploying BIG-IP v14 images.*


## Supported Instance Types and Hypervisors

- For a list of supported Google instance types for this solution, see the [Google instances for BIG-IP VE](https://clouddocs.f5.com/cloud/public/v1/google/Google_singleNIC.html).

- For a list of versions of the BIG-IP Virtual Edition (VE) and F5 licenses that are supported on specific hypervisors and Google Cloud, see [BIG-IP VE Supported Platforms](https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/ve-supported-hypervisor-matrix.html).


## Documentation

For more information on F5 solutions for Google Cloud, including manual configuration procedures for some deployment scenarios, see the Google Cloud section of [Public Cloud Docs](http://clouddocs.f5.com/cloud/public/v1/).


## Getting Help

Due to the heavy customization requirements of external cloud resources and BIG-IP configurations in these solutions, F5 does not provide technical support for deploying, customizing, or troubleshooting the templates themselves. However, the various underlying products and components used (for example: [F5 BIG-IP Virtual Edition](https://clouddocs.f5.com/cloud/public/v1/), [F5 BIG-IP Runtime Init](https://github.com/F5Networks/f5-bigip-runtime-init), [F5 Automation Toolchain](https://www.f5.com/pdf/products/automation-toolchain-overview.pdf) extensions, and [Cloud Failover Extension (CFE)](https://clouddocs.f5.com/products/extensions/f5-cloud-failover/latest/)) in the solutions located here are F5-supported and capable of being deployed with other orchestration tools. Read more about [Support Policies](https://www.f5.com/company/policies/support-policies). Problems found with the templates deployed as-is should be reported via a GitHub issue.

For help with authoring and support for custom CST2 templates, we recommend engaging F5 Professional Services (PS).

### Filing Issues

Use the **Issues** link on the GitHub menu bar in this repository for items such as enhancement or feature requests and bugs found when deploying the example templates as-is. Tell us as much as you can about what you found and how you found it.