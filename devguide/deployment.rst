Deploying Cloud Kotta
=====================

Cloud Kotta infrastructure and code are both Open Source and designed to be reproducible.
The infrastructure is written as a json configuration file using Amazon's CloudFormation, and the various services that run on the infrastructure is written in python. All of this is available on the `github page <https://github.com/yadudoc/cloud_kotta>`_. This docs page will cover the steps to deploy an instance of Cloud Kotta.

1. Launching CloudFormation
---------------------------

1. Git clone the `cloud_kotta <https://github.com/yadudoc/cloud_kotta>`_ repo.

2. Make sure you have admin privileges on AWS

3. Go to `cloudformation console for launch stack <https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new>`_

4. Select *Upload a template to Amazon S3* and select the **Cloud_Kotta_Base.json** file from cloud_kotta/infrastructure/Cloud_Kotta_Base.json and click **Next**

5. Name the stack, and specify a short and sweet name for the JobsBucket. Please note that the name of the bucket specified
   should match the S3 naming conventions and also be globally unique.

6. Click **Next** to launch.

7. Once the stack has been launched without errors, check the outputs from the outputs tab in the CloudFormation console
to see details of the various services that have been launched.

2. Launching Kotta-Base
-----------------------

The Kotta launch process starts with launching the Kotta base cloudformation document. This cloudformation
document launches the persistent data-stores and the roles that will be necessary by the main kotta setup.

This setup will launch the following :

1. **JobsBucket**  : This is the S3 bucket designated for storing uploads, outputs generated, and the code store
   for deploying private repos. All custom changes to the kotta system codebase will be stored on this bucket
for deployment.

2. **JobsTable**  : This is the DynamoDB table that holds all the job information. Several Kotta stacks can
   be served from a single tables without losing any history.

3. **UsersTable** : This is the DynamoDB table that holds all the user information. This needs to be manually
   popoluated for a fresh kotta setup.

4. **Roles** : The kotta base cloudformation document will also setup the appropriate roles for the WebServer
and the TaskExecutor.

5. **Policies** : Access policies for the above roles to the JobsBucket are also created.

3. Custom Changes to your Kotta Stack
-------------------------------------

In order to make custom changes to the stack, git clone the cloud_kotta repo and make appropriate
changes to cloud_kotta/web2 directory. Update the production.conf and the pages under cloud_kotta/web2/views.

Once changes have been made, tar ball the directory and push to the S3 Jobs bucket.

.. code-block:: bash

   git clone https://github.com/yadudoc/cloud_kotta.git
   # Make changes to cloud_kotta/web2 configs and web views.
                ....
   # Make the tarball
   tar -cvzf cloud_kotta.tar.gz cloud_kotta

   # Upload to JobsBucket. 
   aws s3 cp cloud_kotta.tar.gz s3://<Your_Jobs_Bucket_Name>/code/

   


1. Set Region
-------------

Please ensure that all your tests are done in the AWS North Virginia Region. This is required to ensure that the AMI's used in the cloudformation documents are valid and available. With more testing and usage, the cloudformation document will support other regions and/or potentially multiple regions but that is a capability this system currently lacks.

Steps to change region on Web Console :

1. Login to your AWS web console
2. The regions are listed in a dropdown on the top right corner.
3. Select N.Virginia from the dropdown

Alternatively, load this URL which specifies the region, us-east-1 which represents N.Virginia
after logging into the web console: `<https://console.aws.amazon.com/console/home?region=us-east-1#>`_

To read more : `AWS Regions and availability zones <http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html>`_


2. Register a Domain
--------------------

It is nice to have a domain registered and use that with the next step. To setup a domain name the simplest solution is to use Amazon's Route 53 service.
This also allows the creation of a HTTPS SSL cert using the AWS certificat manager that could be used to provide HTTPS access to the web interface.

Here's documentation on how to register a domain : `<http://docs.aws.amazon.com/Route53/latest/DeveloperGuide/domain-register.html>`_


3. Login with Amazon
--------------------

Cloud Kotta relies on Amazon's OAuth2 implementation, Login with Amazon for handling user authentication.

Follow steps here: `Register Documentation <http://login.amazon.com/website>`_

As you finish the registration process, ensure that you note down the Client-ID and secret

4. Create a certificate
-----------------------

The Amazon certificate manager allows you to create certificates for your domain that can be used with Elastic Load Balancers.
Go to `<https://console.aws.amazon.com/acm/home?region=us-east-1#/>`_ and follow steps outlined here to get a certificate:
`<https://aws.amazon.com/certificate-manager/getting-started/>`_. This is a fairly simple process as the request certificate button
takes you to a wizard. In this step you create are requesting a managed certificate used by web browsers to verify the authenticity
of your website with a 3rd party (AWS in this case).

Once a certificate is generated, get the ARN for the certificate. This is to be passed to the Cloud formation form during the Cloud Kotta deployment phase.
This certifate is a managed SSL certificate used to terminate SSL connections at the Elastic Load Balancer. This allows us to have SSL from the user to the
network, and plain HTTP from the Load balancer to the Webserver.


5. Launch the Base
------------------

Kotta base setup creates the following :

1. Jobs DB : The database that holds the jobs information
2. Users DB : A database that holds user information
3. WebServer Role : Web server role with the appropriate permissions
4. Worker Role : Worker role with appropriate perms
5. Jobs Bucket : The default bucket where job data, uploads etc are stored


6. Launch Kotta
---------------

Launch the Kotta cloudformation document.
