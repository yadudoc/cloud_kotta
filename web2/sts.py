#!/usr/bin/env python

import time
import boto3

# The calls to AWS STS AssumeRole must be signed with the access key ID
# and secret access key of an existing IAM user or using existing temporary 
# credentials. (You cannot call AssumeRole with the access key for the root 
# account.) The credentials can be in environment variables or in a 
# configuration file and will be discovered automatically by the 
# boto3.client() function. For more information, see the Python SDK 
# documentation: http://boto3.readthedocs.org/en/latest/guide/sqs.html


def get_temp_creds(role_arn):
    # create an STS client object that represents a live connection to the 
    # STS service
    sts_client = boto3.client('sts')

    session_name = "Temp_session_{0}".format(int(time.time()))
    
    # Call the assume_role method of the STSConnection object and pass the role
    # ARN and a role session name.
    assumedRoleObject = sts_client.assume_role(RoleArn=role_arn,
                                               RoleSessionName=session_name)
                                           

    credentials = assumedRoleObject['Credentials']
    return credentials


def get_temp_creds_from_web_identity(role_arn, token, client_id):
    sts_client = boto3.client('sts')
    creds = sts_client.assume_role_with_web_identity(RoleArn=role_arn,
                                                     RoleSessionName="FooSession",
                                                     WebIdentityToken=token,
                                                     ProviderId="www.amazon.com",
                                                     DurationSeconds=3600)
    return creds
    

def print_creds(creds):
    print "Expiration : ", creds["Expiration"]
    print "Key Id     : ", creds["AccessKeyId"]
    print "Secret Key : ", creds["SecretAccessKey"]
    print "Token      : ", creds["SessionToken"]



# This test continues to fail. I do not know why.
# * Needs new tokens when testing.
def test_web_identity():
    token     = "Atza|IQEBLjAsAhQYkhVyWkVS9C9SwodMeqpTORKqhgIUKpyuEBVc1t7qfy9nAdJ1OrRxd0HTiAHBdy9pliwTVUDB7AUdCJgQltlw05g4WcECVX1pCVvBcRTQZOzJSVLixiuUnurZTFkRIbGiUVI_PgIX8pBGeQyKY9l3KyiTTngUzTAxQh4Sd9DwYy--LY9MTGDKJI6RIFbo4PnZVpmV6QGul4LKWB4rOesh8txR0K2MclsCEf5HfI8i63VEB0YjKsBnLkP7iGneIwEyZoRgToOkwMUFDoO1ygjZc48qWEMxxWL-Wxp4BVZGkIQ0XitNahcYWX_n8OPchUfeMFJTaG1ITkV7xl0T1CQAxt46wLdPX6Wj7GKsOm2DpRfCyDbeHeER7SqucyH8PNJr0Qr5qYiDlfdtew"
    client_id = "amzn1.application-oa2-client.57a1520802fa47d9a1ebd0536d0c29a3"
    role_arn = "arn:aws:iam::968994658855:role/Turing_Federator"

    print creds;

if __name__ == "__main__" :

    print "Running STS tests:"
    # From the response that contains the assumed role, get the temporary 
    # credentials that can be used to make subsequent API calls

    role_pfx = "arn:aws:iam::968994658855:role/"
    roles    = ["klab_public", "wos_read_access", "jstor_access", "god_mode"]
    
    for role in roles:
        credentials = get_temp_creds(role_pfx+role)
        print_creds(credentials)


        # Use the temporary credentials that AssumeRole returns to make a 
        # connection to Amazon S3  
        s3_resource = boto3.resource(
            's3',
            aws_access_key_id = credentials['AccessKeyId'],
            aws_secret_access_key = credentials['SecretAccessKey'],
            aws_session_token = credentials['SessionToken'],
        )

        # Use the Amazon S3 resource object that is now configured with the 
        # credentials to access your S3 buckets. 
        for bucket in s3_resource.buckets.all():
            print(bucket.name)
