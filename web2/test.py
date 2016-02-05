#!/usr/bin/env python
import json
import requests
import logging
import config_manager as cm
import boto
import boto.iam
import identity as i
import sns_sqs



app = cm.load_configs("production.conf")

def test_iam(app):

    iam = boto.iam.connect_to_region(app.config["identity"]['region'],
                                     aws_access_key_id=app.config['keys.key_id'],
                                     aws_secret_access_key=app.config['keys.key_secret'],
                                     security_token=app.config['keys.key_token'])
    roles = iam.list_roles();
    print type(roles)
    for role in roles["list_roles_response"]["list_roles_result"]["roles"]:
        print role
        print 

    users =  iam.get_all_users();
    for user in users.items():
        print 
        print user

def list_buckets(app):
    s3 = app.config["s3.conn"]
    print s3.get_all_buckets()

def print_tags(app):
    for k in  app.config["instance.tags"]:
        print "{0}   : {1}".format(k, app.config["instance.tags"][k])


def test_sns(app):
    print app.config["sns.conn"]
    print app.config["instance.tags"]["ProdJobsSNSTopicARN"]
    #sns_sqs.sns_test(app.config["sns.conn"], app.config["instance.tags"]["ProdJobsSNSTopicARN"])

#test_sns(app)
#print_tags(app)


list_buckets(app)
