#!/usr/bin/env python
import json
import requests
import logging
import uuid
from boto.dynamodb2.fields import HashKey
from boto.dynamodb2.table import Table
import boto.dynamodb2 as ddb
import dynamo_utils as dutils
import config_manager as cm
import argparse
import bottle

def load_config(filename):
    app = bottle.default_app()
    try:
        app.config.load_config(filename)
    except Exception as e:
        logging.error("Exception {0} in load_config".format(e))
        exit(-1)
    return app

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

def verify_email_address(app, email):

    ses  = app.config["ses.conn"]
    data = ses.list_verified_email_addresses()
    if data :
        emails = data["ListVerifiedEmailAddressesResponse"]["ListVerifiedEmailAddressesResult"]["VerifiedEmailAddresses"]
        if email not in emails:
            cm.verify_email(app, email)

    else:
        print "Unable to fetch list of verified emails"
        return

import MySQLdb as mysqldb
        
def update_db(app, statements):
    # Execute on all DBs
    for db in ["wos1", "wos2"]:

        print "Connecting to {0} as {1}".format(app.config["database.{0}.passwd".format(db)], 
                                                app.config["database.{0}.url".format(db)])
        db = mysqldb.connect(host = app.config["database.{0}.url".format(db)],
                             port = int(app.config["database.{0}.port".format(db)]),
                             user = app.config["database.{0}.user".format(db)],
                             passwd = app.config["database.{0}.passwd".format(db)])
                         
        cursor = db.cursor()
        for line in statements:
            cursor.execute(line)
            for row in cursor.fetchall():
                print row[0]
            
        db.close()

    return

def create_user(app):    
    print "Updating wos username and passwd"
    
    try:
        cmd = ["DROP USER '{0}'@'%' ;".format(app.config["wos_user"])]
        update_db(app, cmd)
    except Exception, e:
        print "MYSQL threw an error from attempting DROP USER : ", e
        
    print app
    print app.config["wos_user"]
    print app.config["wos_passwd"]
    cmd = ["CREATE USER '{0}'@'%' IDENTIFIED BY '{1}' ;".format(app.config["wos_user"], 
                                                                app.config["wos_passwd"]),
           "GRANT SELECT ON wos.* TO '{0}'@'%' ;".format(app.config["wos_user"])]
    update_db(app, cmd)
    return 

    
if __name__ == "__main__":

    parser   = argparse.ArgumentParser()
    parser.add_argument("-c", "--conffile", default="production.conf", help="Config file path. Defaults to ./test.conf")
    parser.add_argument("-w", "--webofscience", default=None, help="Config file path for webofscience")
    parser.add_argument("-u", "--user_id", required=True, help="Amazon user id");
    parser.add_argument("-n", "--name", help="Name of new user,in quotes");
    parser.add_argument("-e", "--email", help="Email address of new user");
    parser.add_argument("-r", "--role", help="Role to assign to new user");   
    args   = parser.parse_args()

    app = cm.load_configs(args.conffile)

    if args.webofscience :
        w = load_config(args.webofscience)


    app.config["wos_user"]   = args.name.replace(' ', '').lower()
    app.config["wos_passwd"] = str(uuid.uuid4()).replace('-', '')[0:20]

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
            verify_email_address(app, args.email)

        if args.role != None and args.role != user["role"]:
            print "Mismatch in Role : Arg:{0}  DB:{1}".format(args.role, user["role"])
            user["role"] = args.role

        if args.webofscience:            
            print "Updating wos username and passwd"
            user["wos_user"]   = app.config["wos_user"]
            user["wos_passwd"] = app.config["wos_passwd"]
            create_user(app)

        status = dyno.put_item(data=user, overwrite=True)
        print "Update user status : {0}".format(status)
        exit(0)

    else:
        # Creating new user:
        user = {'user_id' : args.user_id,
                'name'    : args.name,
                'email'   : args.email,
                'role'    : args.role}

        if args.webofscience :        
            user["wos_user"]   = app.config["wos_user"]
            user["wos_passwd"] = app.config["wos_passwd"]
            create_user(app)

        verify_email_address(app, args.email)
        status = dyno.put_item(data=user, overwrite=True)
        print "Create user status : {0}".format(status)

    exit(0)
    
