# REST Client for TuringCompute

This is documentation for the REST client that can be used to manage jobs on the TuringCompute platform.


## Access to the Bastion Host

Once you have setup an account with TuringCompute shoot an email to yadunand@uchicago.edu with your
ssh public key to grant you a login account on bastion.turingcompute.net. This is where you'll be
using the REST client to manage jobs on  Turing Compute. 

## Getting started

In order to use the REST_client the only python package that needs to be installed is the requests package.
Here are the steps to get install dependencies and get the requisite code.

```bash
sudo pip install requests
git clone https://github.com/yadudoc/task_engine
cd REST_client
```

## Auth

With the security constraints associated with the data stored on the various storage systems, the REST
client requires you to have a valid access_token from logging in with amazon stored in a file. These
tokens generally expire in 1 hour. You can always do a relogin on turingcompute to get a URL with a
valid access_token. However this does limit scriptability/automation. 

Here are the steps to get this temporary access_token:

1. Go to https://turingcompute.net/login
2. Click Login with Amazon button, and login using credentials that have been registered with TuringCompute
   which will take you to the Login Success page.
3. Copy the complete url from your address bar from the Login Success page to a file.



* One potential solution to getting long living tokens is to use the authorization code grant method:
https://developer.amazon.com/public/apis/engage/login-with-amazon/docs/authorization_grants.html


