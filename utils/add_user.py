#!/usr/bin/env python
import json
import requests
import logging
from boto.dynamodb2.fields import HashKey
from boto.dynamodb2.table import Table
import boto.dynamodb2 as ddb
import dynamo_utils as dutils
import config_manager as cm
import argparse

def connect(app):
    table_name = app.config['dynamodb.turing_users']
    hashkey    = "user_id"
    dyno = Table(table_name,
                 schema=[HashKey(hashkey)],
                 connection=ddb.connect_to_region(app.config['dynamodb.region'],
                                                  aws_access_key_id=app.config['keys.key_id'],
                                                  aws_secret_access_key=app.config['keys.key_secret'],
                                                  security_token=app.config['keys.key_token']))
    return dyno

def find_user_role(app, dyno, user_id):
    try:
        results = dyno.get_item(user_id=user_id)
    except ddb.exceptions.ItemNotFound:
        return None

    return results



if __name__ == "__main__":

    parser   = argparse.ArgumentParser()
    parser.add_argument("-c", "--conffile", default="production.conf", help="Config file path. Defaults to ./test.conf")
    parser.add_argument("-u", "--user_id", required=True, help="Amazon user id");
    parser.add_argument("-n", "--name", help="Name of new user,in quotes");
    parser.add_argument("-e", "--email", help="Email address of new user");
    parser.add_argument("-r", "--role", help="Role to assign to new user");   
    args   = parser.parse_args()

    app = cm.load_configs(args.conffile)
    print args.user_id
    print args.name
    print args.email
    print args.role

    dyno = connect(app)

    user = find_user_role(app, dyno, args.user_id)
    if user != None:
        print "User exists "
        if args.name != None and args.name != user["name"]:
            print "Mismatch in Name : Arg:{0}  DB:{1}".format(args.name, user["name"])
            user["name"] = args.name
            
        if args.email != None and args.email != user["email"]:
            print "Mismatch in Email: Arg:{0}  DB:{1}".format(args.email, user["email"])
            user["email"] = args.email

        if args.role != None and args.role != user["role"]:
            print "Mismatch in Role : Arg:{0}  DB:{1}".format(args.role, user["role"])
            user["role"] = args.role

        status = dyno.put_item(data=user, overwrite=True)
        print "Update user status : {0}".format(status)
        exit(0)
        
    user = {'user_id' : args.user_id,
            'name'    : args.name,
            'email'   : args.email,
            'role'    : args.role}

    status = dyno.put_item(data=user, overwrite=True)
    print "Create user status : {0}".format(status)
    exit(0)
    
