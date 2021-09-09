# Deploying the BIG-IP VE in GCP - Example Autoscale BIG-IP WAF (LTM + ASM) - Managed Instance Group (Frontend via ALB) - PAYG Licensing

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
  - [Deploying this Solution](#deploying-this-solution)
    - [Deploying via the gcloud CLI](#deploying-via-the-gcloud-cli)
    - [Changing the BIG-IP Deployment](#changing-the-big-ip-deployment)
  - [Validation](#validation)
    - [Validating the Deployment](#validating-the-deployment)
    - [Testing the WAF Service](#testing-the-waf-service)
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

This solution uses a parent template to launch several linked child templates (modules) to create a full example stack for the BIG-IP Autoscale solution. The linked templates are located in the examples/modules directories in this repository. **F5 recommends you clone this repository and modify these templates to fit your use case.** 

The modules below create the following resources:

- **Network**: This template creates Virtual Networks, Subnets, and Route Tables.
- **Application**: This template creates a generic example application for use when demonstrating live traffic through the BIG-IPs.
- **Disaggregation** *(DAG/Ingress)*: This template creates resources required to get traffic to the BIG-IP, including Firewalls, Forwarding Rules, internal/external Load Balancers, and accompanying resources such as health probes.
- **Access**: This template creates a custom IAM role for the BIG-IP instances and other resources to gain access to Google Cloud services such as compute and storage.
- **BIG-IP**: This template creates compute instances with F5 BIG-IP Virtual Editions provisioned with Local Traffic Manager (LTM) and Application Security Manager (ASM). Traffic flows from the Google load balancer to the BIG-IP VE instances and then to the application servers. The BIG-IP VE(s) are configured in single-NIC mode. Auto scaling means that as certain thresholds are reached, the number of BIG-IP VE instances automatically increases or decreases accordingly. The BIG-IP module template can be deployed separately from the example template provided here into an "existing" stack.

This solution leverages traditional Autoscale configuration management practices where each instance is created with an identical configuration as defined in the model. The BIG-IP's configuration, now defined in a single convenient YAML or JSON [F5 BIG-IP Runtime Init](https://github.com/F5Networks/f5-bigip-runtime-init) configuration file, leverages [F5 Automation Tool Chain](https://www.f5.com/pdf/products/automation-toolchain-overview.pdf) declarations which are easier to author, validate and maintain as code. For instance, if you need to change the configuration on the BIG-IPs in the deployment, instead of updating the existing instances directly, you update the instance model by passing a new config file (which references the updated Automation Toolchain declarations) via template's bigIpRuntimeInitConfig input parameter. The model will be responsible for maintaining the configuration across the deployment, updating existing instances and deploying new instances with the latest configuration.


## Diagram

![Configuration Example](diagram.png)


## Prerequisites

  - This solution requires a Google Cloud account that can provision objects described in the solution using the gcloud CLI:
      ```bash
      gcloud deployment-manager deployments create ${DEPLOYMENT_NAME} --template ${TEMPLATE_FILE} --properties ${PROPERTIES}
      ```
  - This solution requires an [SSH key](https://cloud.google.com/compute/docs/instances/adding-removing-ssh-keys) for access to the BIG-IP instances.
  - This solution requires you to accept any Google Cloud Marketplace "License/Terms and Conditions" for the images used in this solution.
    - By default, this solution uses [F5 Advanced WAF with LTM, IPI and TC (PAYG - 25Mbps)](https://console.cloud.google.com/marketplace/product/f5-7626-networks-public/f5-big-awf-plus-pve-payg-25mbps)


## Important Configuration Notes

- By default, this solution does not create a custom BIG-IP WebUI user as instances are not intended to be managed directly. However, an SSH key is installed to provide CLI access for demonstration and debugging purposes. 
  - **Disclaimer:** ***Accessing or logging into the instances themselves is for demonstration and debugging purposes only. All configuration changes should be applied by updating the model via the template instead.***
  - See [Changing the BIG-IP Deployment](#changing-the-big-ip-deployment) for more details.

- This solution requires Internet access for: 
  1. Downloading additional F5 software components used for onboarding and configuring the BIG-IP (via github.com). *NOTE: access via web proxy is not currently supported. Other options include 1) hosting the file locally and modifying the runtime-init package url and configuration files to point to local URLs instead or 2) baking them into a custom image (BYOL images only), using the [F5 Image Generation Tool](https://clouddocs.f5.com/cloud/public/v1/ve-image-gen_index.html).*
  2. Contacting native cloud services for various cloud integrations: 
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

| Parameter | Required | Description |
| --- | --- | --- |
| appContainerName | No | The name of a container to download and install which is used for the example application server. If this value is left blank, the application module template is not deployed. |
| application | No | Application label. |
| availabilityZone | Yes | Enter the availability zone where you want to deploy the application, for example 'us-west1-a'. |
| bigIpRuntimeInitPackageUrl | Yes | Supply a URL for the bigip-runtime-init package |
| bigIpRuntimeInitConfig | Yes | Supply a URL to the bigip-runtime-init configuration file in YAML or JSON format, or an escaped JSON string to use for f5-bigip-runtime-init configuration. |
| coolDownPeriodSec | No | The application initialization period; the autoscaler uses the cool down period for scaling decisions. |
| cost | No | Cost Center label. |
| environment | No | Environment label. | 
| group | No | Group label. |
| instanceTemplateVersion | No | Version of the instance template to create. When updating deployment properties of the BIG-IP instances, you must provide a unique value for this parameter. |
| instanceType | Yes | Instance type assigned to the application, for example 'n1-standard-1'. |
| imageName | Yes | Name of BIG-IP custom image found in the Google Cloud Marketplace. Example value: `f5-bigip-16-0-1-1-0-0-6-payg-best-200mbps-210129040615`. You can find the names of F5 marketplace images in the README for this template or by running the command: `gcloud compute images list --filter="name~f5"`. |
| maxNumReplicas | No | Maximum number of replicas that autoscaler can provision |
| minNumReplicas | No | Minimum number of replicas that autoscaler can provision |
| owner | No | Owner label. |
| region | Yes | Google Cloud region used for this deployment. |
| restrictedSrcAddressMgmt | Yes | This field restricts management access to specific networks or addresses. Enter an IP address or address range in CIDR notation separated by a space.  **IMPORTANT** This solution requires your Management's subnet at a minimum in order for the peers to cluster.  For example, '10.0.11.0/24 55.55.55.55/32' where 10.0.11.0/24 is your local management subnet and 55.55.55.55/32 is a specific address (ex. orchestration host/desktop/etc.). |
| restrictedSrcAddressApp | Yes | This field restricts web application access to a specific network or address; the port is defined using applicationPort parameter. Enter an IP address or address range in CIDR notation separated by a space. |
| restrictedSrcAddressAppInternal | Yes | This field restricts web application access to a specific private network or address. Enter an IP address or address range in CIDR notation separated by a space. |
| secretId | No | ID of the secret stored in Secret Manager |
| uniqueString | Yes | A prefix that will be used to name template resources. Because some resources require globally unique names, we recommend using a unique value. |
| update | No | Specify true when updating the deployment. |
| utilizationTarget | No | The target value of the metric that autoscaler should maintain. This must be a positive value. A utilization metric scales number of virtual machines handling requests to increase or decrease proportionally to the metric. |

### Template Outputs

| Name | Description | Type |
| --- | --- | --- |
| deployment_name | Name of parent deployment | string |
| appUsername | Application user name | Application Template | string |
| appVmssName | Application Virtual Machine Scale Set name | Application Template | string |
| appVmssId | Application Virtual Machine Scale Set resource ID | Application Template | string |
| bigIpUsername | BIG-IP user name | BIG-IP Template | string |
| virtualNetworkId | Virtual Network resource ID | Network Template | string |
| bigIpVmssId | BIG-IP Virtual Machine Scale Set resource ID | BIG-IP Template | string |
| bigIpVmssName | BIG-IP Virtual Machine Scale Set name| BIG-IP Template | string |
| wafPublicIps | WAF Service Public IP Addresses | DAG Template | array |


## Deploying this Solution

See [Prerequisites](#prerequisites).

To deploy this solution, you must use the [gcloud CLI](#deploying-via-the-gcloud-cli)


### Deploying via the gcloud CLI

To deploy the BIG-IP VE from the parent template YAML file, use the following command syntax:

```gcloud deployment-manager deployments create <your-deployment-name> --config <your-file-name.yaml> --description "<deployment-description>"```

Keep in mind the following:

- Follow the sample_autoscale.yaml file for guidance on what to include in the yaml file, include required imports and parameters
- *your-deployment-name*<br>This name must be unique.<br>
- *your-file-name.yaml*<br>If your file is not in the same directory as the Google SDK, include the full file path in the command.



### Changing the BIG-IP Deployment

You will most likely want or need to change the BIG-IP configuration. This generally involves referencing or customizing a [F5 BIG-IP Runtime Init](https://github.com/F5Networks/f5-bigip-runtime-init) configuration file and passing it through the **bigIpRuntimeInitConfig** template parameter as a URL or inline json. 

Example from sample_autoscale.yaml
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

*TIP: If you don't have an easy way to host your own config files, passing the config as inline json via the template input parameter might be the quickest / most accessible option to test out different BIG-IP configs using this repository.*
 
F5 has provided the following example configuration files in the `examples/autoscale/bigip-configurations` folder:

- `runtime-init-conf-bigiq.yaml` - This configuration file installs packages and creates WAF-protected services for a BIG-IQ licensed deployment based on the Automation Toolchain declaration URLs listed above.
- `runtime-init-conf-payg.yaml` - This inline configuration file installs packages and creates WAF-protected services for a PAYG licensed deployment.
- `Rapid_Deployment_Policy_13_1.xml` - This ASM security policy is supported for BIG-IP 13.1 and later.

See [F5 BIG-IP Runtime Init](https://github.com/F5Networks/f5-bigip-runtime-init) for more examples. 
 
By default, this solution deploys the `runtime-init-conf-payg.yaml` configuration. 

This example configuration does not require any modifications to deploy successfully *(Disclaimer: "Successfully" implying the template deploys without errors and deploys BIG-IP WAFs capable of passing traffic. To be fully functional as designed, you would need to have satisfied the [Prerequisites](#prerequisites))* However, in production, these files would commonly be customized. Some examples of small customizations or modifications are provided below. 

The example AS3 declaration in this config uses [Service Discovery](https://clouddocs.f5.com/products/extensions/f5-appsvcs-extension/latest/userguide/service-discovery.html#using-service-discovery-with-as3) to populate the pool with the private IP addresses of application servers in a instance group. By default, the fields for the service discovery configuration (**resourceGroup**, **subscriptionId** and ***uniqueString***) are rendered similarly from Google Cloud metadata. If the application instance group is located in a different resource group or subscription, you can modify these values. 

To change the Pool configuration:

  1. edit/modify the AS3 Declaration (AS3) declaration in a corresponding runtime-init config file with the new `Pool` values. 

Example:
```yaml
              class: Pool
              remark: Service 1 shared pool
              members:
                - addressDiscovery: gce
                  addressRealm: private
                  region: us-west1
                  servicePort: 80
                  updateInterval: 60
```

  - *NOTE:* 
    - The managed identity assigned to the BIG-IP VE instance(s) must have read permissions on the managed instance group resource.
    - The Service Discovery configuration listed above targets a specific managed instance group ID to reduce the number of requests made to the Google Cloud API endpoints. When choosing capacity for the BIG-IP VE and application instance group, it is possible to exceed the API request limits. Consult the Google Compute Engine API rate limits [documentation](https://cloud.google.com/compute/docs/api-rate-limits) for more information.

  - Or even with another pool configuration entirely. For example, using the [FQDN](https://clouddocs.f5.com/products/extensions/f5-appsvcs-extension/latest/declarations/discovery.html#using-an-fqdn-pool-to-identify-pool-members) Service Discovery instead to point to a DNS name.

```yaml
              class: Pool
              remark: Service 1 shared pool
              members:
              - addressDiscovery: fqdn
                autoPopulate: true
                hostname: <WWW.YOURSITE.COM>
                servicePort: 80
```

  2. Publish/host the customized runtime-init config file at a location reachable by the BIG-IP at deploy time (for example, GitHub, Google Cloud Storage, etc.) or render/format to send as inline json.
  3. Update the **bigIpRuntimeInitConfig** input parameter to reference the new URL or inline json of the updated configuration 
  4. Deploy or Re-Deploy


## Validation

This section describes how to validate the template deployment, test the WAF service, and troubleshoot common problems.


### Validating the Deployment

To view the status of the example and module template deployments, navigate to **Deployment Manager > *Deployments* > *Deployment Name***. You should see a series of deployments, including one each for the example template as well as the access, application, network, dag, and bigip templates. The deployment status for the parent template deployment should indicate that the template has been successfully deployed.

Expected Deploy time for entire stack =~ 8-10 minutes.

If any of the deployments are in a failed state, proceed to the [Troubleshooting Steps](#troubleshooting-steps) section below.

### Testing the WAF Service

To test the WAF service, perform the following steps:
- Check the instance group health state; instance health is based on Google Cloud's ability to connect to your application via the instance group's load balancer
  - The health state for each instance should be "Healthy". If the state is "Unhealthy", proceed to the [Troubleshooting Steps](#troubleshooting-steps) section.
- Obtain the IP address of the WAF service:
  - **gcloud CLI**: 
      ```bash
      gcloud compute forwarding-rules describe ${forwarding_rule} --region=${region} --format='value(IPAddress)'
      ```
- Verify the application is responding:
  - Paste the IP address in a browser: ```https://${IP_ADDRESS_FROM_OUTPUT}```
      - NOTE: By default, the Virtual Service starts with a self-signed cert. Follow your browsers instructions for accepting self-signed certs (for example, if using Chrome, click inside the page and type this "thisisunsafe". If using Firefox, click "Advanced" button, Click "Accept Risk and Continue", etc.).
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

### Accessing the BIG-IP

- Obtain the IP address of the BIG-IP Management Port:

  - **gcloud CLI**: 
    - Public IPs: 
      ```shell
      gcloud compute instances describe ${instance} --zone=${zone} --format='value(networkInterfaces.networkIP)'
      ```
    - Private IPs: 
      ```shell 
      gcloud compute instances describe ${instance} --zone=${zone} --format='value(networkInterfaces.accessConfigs[0].natIP)'
      ```
- Login in via SSH:
  - **SSH key authentication**: 
    ```bash
    ssh admin@${IP_ADDRESS_FROM_OUTPUT} -i ${YOUR_PRIVATE_SSH_KEY}
    ```

- Login in via WebUI:
  - As mentioned above, no password is configured by default. If you would like or need to login to the GUI for debugging or inspection, you can create a custom username/password by logging in to admin account via SSH (per above) and use tmsh to create one:
    At the TMSH prompt ```admin@(ip-10-0-0-100)(cfg-sync Standalone)(Active)(/Common)(tmos)#```:
      ```shell
      create auth user <YOUR_WEBUI_USERNAME> password <YOUR_STRONG_PASSWORD> partition-access add { all-partitions { role admin } }

      save sys config
      ```

  - Open a browser to the Management IP
    - ```https://${IP_ADDRESS_FROM_OUTPUT}:8443```
    - NOTE: 
      - By default, for Single NIC deployments, the management port is 8443.
      - By default, the BIG-IP's WebUI starts with a self-signed cert. Follow your browsers instructions for accepting self-signed certs (for example, if using Chrome, click inside the page and type this "thisisunsafe". If using Firefox, click "Advanced" button, Click "Accept Risk and Continue" ).
    - To Login: 
      - username: `<YOUR_WEBUI_USERNAME>`
      - password: `<YOUR_STRONG_PASSWORD>`
      

### Further Exploring

#### WebUI
 - Navigate to **Virtual Services > Partition**. Select Partition = `Tenant_1`
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


## Updating this Solution

### BIG-IP Lifecycle Management

As mentioned in the [Introduction](#introduction), if you need to change the configuration on the BIG-IPs in the deployment, instead of updating the existing instances directly, you update the instance model by passing a new config file (which references the updated Automation Toolchain declarations) via template's bigIpRuntimeInitConfig input parameter. The model will be responsible for maintaining the configuration across the deployment, updating existing instances and deploying new instances with the latest configuration.

This happens by leveraging Google Cloud's Managed Instance Group's [automatic rolling out](https://cloud.google.com/compute/docs/instance-groups/rolling-out-updates-to-managed-instance-groups) feature.

By default, Rolling Upgrades are configured to upgrade in batches of 20% with zero pause time in between sets and minimum of 20% of healthy nodes available. To modify, you can customize the `/module/bigip-autoscale` template.

#### Updating the Configuration

1. Modify the **bigIpRuntimeInitConfig** parameter value to trigger a model update. If using inline json, make a configuration change in parameter payload. If using a URL, reference a new URL. Example:
  - If using tags for versions, change from `v1.2.0.0`
    ```json
        "bigIpRuntimeInitConfig": {
          "value": "https://raw.githubusercontent.com/F5Networks/f5-google-gdm-templates-v2/v1.2.0.0/examples/autoscale/bigip-configurations/runtime-init-conf-payg.yaml"
        },
    ```
    to `v1.3.1.0`
    ```json
        "bigIpRuntimeInitConfig": {
          "value": "https://raw.githubusercontent.com/F5Networks/f5-google-gdm-templates-v2/v1.3.1.0/examples/autoscale/bigip-configurations/runtime-init-conf-payg.yaml"
        },
    ```
2. Modify the **update** parameter to True. This removes dependencies that are required for the initial deployment only.
3. Modify the **instanceTemplateVersion** parameter to 2 (or a subsequent version number if you have redeployed multiple times). Specifying a unique value causes the deployment to create a new instance template for the VM instances.
4. Re-deploy the template with new **bigIpRuntimeInitConfig** parameter updated in your configuration file.
    ```bash
    gcloud deployment-manager deployments update <your-deployment-name> --config <your-file-name.yaml> --description "<deployment-description>"
    ```  

#### Upgrading the BIG-IP VE Image
As new BIG-IP versions are released, existing Managed Instance Groups can be upgraded to use those new images with same procedure. 

1. Modify the **bigIpImage** input parameter value to new BIG-IP version in your configuration file.

2. Re-deploy the template with new **bigIpImage** parameter.
    ```bash 
    gcloud deployment-manager deployments update <your-deployment-name> --config <your-file-name.yaml> --description "<deployment-description>"
    ```  

#### Lifecycle Troubleshooting

If a new configuration update fails (for example, invalid config, typo, etc.) and Rolling Upgrade fails to complete.

1. [Stop](https://cloud.google.com/sdk/gcloud/reference/deployment-manager/deployments/stop) any hung Deployments
    - **gcloud CLI**: 
        ```bash 
        gcloud deployment-manager deployments stop ${DEPLOYMENT_NAME}
        ```
2. [Stop](https://cloud.google.com/deployment-manager/docs/deployments/updating-deployments#stop_an_update) any updates in progress
    - **gcloud CLI**: 
      ```bash 
      gcloud deployment-manager deployments stop ${DEPLOYMENT_NAME}
      ```
3. Modify parameters to update the model.
    - Modify the parameter that resulted in failure (for example, a previous or working **bigIpRuntimeInitConfig** value or image).
    - Modify Scaling Size to deploy new instances .
      - Increase **minNumReplicas** parameter value by 1 or more.
4. Re-deploy the template with new parameter values ( the failed parameter and **minNumReplicas**).
5. Confirm newly instantiated instance(s) are "Healthy".
6. [Delete](https://cloud.google.com/sdk/gcloud/reference/compute/instances/delete) failed instances.
    - **gcloud CLI**: 
      ```bash 
      gcloud compute instances delete ${INSTANCE_NAME} --zone=${ZONE_NAME}
      ```


## Deleting this Solution

### Deleting the deployment via Google Cloud Console 

1. Navigate to **Deployment Manager** > Select "Deployments" Icon.

2. Select your parent template deployment by clicking the check box next to the deployment name.

3. Click **Delete**.

4. Choose an option for retaining template resources.

5. Click **Delete All** to confirm.

### Deleting the deployment using the gcloud CLI

Before deleting this solution, if you had previously updated the deployment, you must first redeploy while specifying "False" for the update input parameter in your configuration file:

```bash
    gcloud deployment-manager deployments update <your-deployment-name> --config <your-updated-file-name.yaml>
```

Do not change the instanceTemplateVersion input parameter value when redeploying before delete.

After redeploying with update:false, you can delete the deployment without dependency errors:

```bash
  gcloud deployment-manager deployments delete <your-deployment-name> -q
```


### Troubleshooting Steps

There are generally two classes of issues:

1. Template deployment itself failed
2. Resource(s) within the template failed to deploy

To verify that all templates deployed successfully, follow the instructions under **Validating the Deployment** above to locate the failed deployment(s).

Click on the name of a failed deployment and then click Events. Click the link in the red banner at the top of the deployment overview for details about the failure cause. 

Additionally, if the template passed validation but individual template resources have failed to deploy, you can see more information by expanding Deployment Details, then clicking on the Operation details column for the failed resource. **When creating a GitHub issue for a template, please include as much information as possible from the failed Google Cloud deployment/resource events.**

Common deployment failure causes include:
- Required fields were left empty or contained incorrect values (input type mismatch, prohibited characters, malformed YAML, etc.) causing template validation failure
- Insufficient permissions to create the deployment or resources created by a deployment
- Resource limitations (exceeded limit of IP addresses or compute resources, etc.)
- Google Cloud service issues (these will usually surface as 503 internal server errors in the deployment status error message)

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

| Google Cloud BIG-IP Image Version | BIG-IP Version |
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
