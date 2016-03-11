#!/usr/bin/env python
import json
import requests
import logging
from boto.dynamodb2.fields import HashKey
from boto.dynamodb2.table import Table
import boto.dynamodb2 as ddb
import dynamo_utils as dutils

def get_identity_from_token(access_token, client_id):

    result = requests.get("https://api.amazon.com/auth/o2/tokeninfo?access_token=" + access_token)
    if result.status_code != 200 :
        print "Failed to verify origin of authentication token"
        logging.error("Failed to verify origin of authentication token")
        return None, None, "Failed to verify origin of authentication token"

    if result.json()['aud'] != client_id:
        print "Error: Blocking attempt to subvert authentication token"
        return None, None, "Error: Blocking attempt to subvert authentication token"

    headers = {'Authorization' : 'bearer ' + access_token}
    result = requests.get("https://api.amazon.com/user/profile?access_token=" + access_token, headers=headers)
    if result.status_code != 200 :
        print "Error: Failed to verify User"
        return None, None, "Failed to verify user"

    r = result.json()
    print r
    return r['user_id'], r['name'], r['email']


def connect_to_users_db(app):

    table_name = app.config['dynamodb.turing_users']
    hashkey    = "user_id"
    #dyno = dutils.connect_to_db(app, app.config['dynamodb.turing_users'], "user_id")
    dyno = Table(table_name,
                 schema=[HashKey(hashkey)],
                 connection=ddb.connect_to_region(app.config['dynamodb.region'],
                                                  aws_access_key_id=app.config['keys.key_id'],
                                                  aws_secret_access_key=app.config['keys.key_secret'],
                                                  security_token=app.config['keys.key_token']))

    results = dyno.scan()
    print "-"*50
    for r in results:
        print "User: {0}  Role: {1}".format(r["user_id"], r["role"])
    return results

def find_user_role(app, user_id):

    table_name = app.config['dynamodb.turing_users']
    hashkey    = "user_id"
    dyno = Table(table_name,
                 schema=[HashKey(hashkey)],
                 connection=ddb.connect_to_region(app.config['dynamodb.region'],
                                                  aws_access_key_id=app.config['keys.key_id'],
                                                  aws_secret_access_key=app.config['keys.key_secret'],
                                                  security_token=app.config['keys.key_token']))


    try:
        results = dyno.get_item(user_id=user_id)
    except ddb.exceptions.ItemNotFound:
        return None

    return results
