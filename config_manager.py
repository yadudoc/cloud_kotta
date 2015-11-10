#!/usr/bin/env python
'''
 Copyright (C) Yadu Nand B <yadudoc1729@gmail.com> - All Rights Reserved
 Unauthorized copying of this file, via any medium is strictly prohibited
 Proprietary and confidential
 Written by Yadu Nand B <yadudoc1729@gmail.com>, September 2015
'''

import os
import logging
import bottle
import requests
import time
from boto.dynamodb2.fields import HashKey
from boto.dynamodb2.table import Table
import boto.dynamodb2 as ddb

log_levels = { "DEBUG"   : logging.DEBUG,
               "INFO"    : logging.INFO,
               "WARNING" : logging.WARNING,
               "ERROR"   : logging.ERROR,
               "CRITICAL": logging.CRITICAL
           }


# Returns true if the credentials were updated
def update_creds_from_metadata_server(app):
    #Todo error check for timeout errors from http access
    #TOdo error catch for json decode failure
    if "keys.expiry" in app.config and app.config["keys.expiry"] > time.time():
        return False

    URL  = app.config["metadata.credurl"]
    role = requests.get(URL).content
    URL  = URL + role
    data = requests.get(URL).json()

    app.config["keys.expiry"]     = time.strptime(str(data['Expiration']), '%Y-%m-%dT%H:%M:%SZ')
    app.config["keys.key_id"]     = str(data['AccessKeyId'])
    app.config["keys.key_secret"] = str(data['SecretAccessKey'])
    app.config["keys.key_token"]  = str(data['Token'])
    return True


def connect_to_dynamodb(app):
    stat = update_creds_from_metadata_server(app)

    # If an entry exists for the table and the credentials have
    # not been updated then skip the connection
    if "dynamodb.table" in app.config and not stat:
        return app

    dbconn = ddb.connect_to_region(app.config['dynamodb.region'],
                                   aws_access_key_id=app.config['keys.key_id'],
                                   aws_secret_access_key=app.config['keys.key_secret'],
                                   security_token=app.config['keys.key_token'])

    dyno = Table(app.config['dynamodb.table_name'],
                 schema=[HashKey("CustomerUUID")],
                 connection=dbconn)

    app.config["dynamodb.table"] = dyno
    return app

def load_configs(filename):
    app = bottle.default_app()
    try:
        app.config.load_config(filename)
    except Exception, e:
        logging.error("Exception {0} in load_config".format(e))
        exit(-1)

    logging.debug("Config : \n {0}".format(app.config))

    for keys in app.config:
        if keys.startswith('keys.'):
            keyfile = app.config[keys].replace('\"', '')

            logging.debug("Keyfile : {0}".format(keyfile.replace('\"', '')))
            if not os.path.isfile(keyfile):
                print "Key file {0} missing!".format(keyfile)
                logging.error("Key file {0} missing!".format(keyfile))
                exit(-1)
            with open(keyfile, 'r') as kf:
                app.config[keys] = kf.read()
                print "keys : ", app.config[keys]

    print "Foo1"
    if 'metadata.credurl' in app.config:
        update_creds_from_metadata_server(app)
    print "Foo2"
    app = connect_to_dynamodb(app)
    return app

