Deploying Cloud Kotta
=====================

Cloud Kotta infrastructure and code are both Open Source and designed to be reproducible.
The infrastructure is written as a json configuration file using Amazon's CloudFormation, and the various services that run on the infrastructure is written in python. All of this is available on the `github page <https://github.com/yadudoc/cloud_kotta>`_. This docs page will cover the steps to deploy an instance of Cloud Kotta.

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
