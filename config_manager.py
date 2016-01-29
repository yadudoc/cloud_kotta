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
import boto.ec2
import boto.sqs
import boto.sns
import boto.ses
from bottle import app, template
from boto.s3.connection import S3Connection
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta

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

    if "keys.expiry" in app.config and app.config["keys.expiry"] > (datetime.now() + relativedelta(hours=1)):
        logging.debug("Update creds from metadata cancelled {0} < {1}".format(
            app.config["keys.expiry"],
            datetime.now()))
        return False

    URL  = app.config["metadata.credurl"]
    role = requests.get(URL).content
    URL  = URL + role
    data = requests.get(URL).json()

    app.config["keys.expiry"]     = datetime.strptime(str(data['Expiration']), '%Y-%m-%dT%H:%M:%SZ')
    app.config["keys.key_id"]     = str(data['AccessKeyId'])
    app.config["keys.key_secret"] = str(data['SecretAccessKey'])
    app.config["keys.key_token"]  = str(data['Token'])

    URL  = app.config["metadata.metaserver"]
    data = requests.get(URL).text
    app.config["instance_id"] = str(data)

    URL  = app.config["metadata.metaserver"]
    data = requests.get(URL+"placement/availability-zone/").text
    app.config["region"] = str(data)

    URL  = app.config["metadata.metaidentity"]
    data = requests.get(URL).json()
    app.config["identity"] = data

    if "doReload" in app.config and app.config["doReload"] == True:
        init(app)

    return True


##################################################################
# Annoy human with email
##################################################################
def send_success_mail(data, app):
    sesconn     =  app.config['ses.conn']
    job_id      =  data.get('job_id')
    rec_email   =  data.get('user_email')
    rec_name    =  data.get('friendly_name') #data.get('username')
    src_email   =  app.config['ses.email_sender']
    url         =  app.config['server.url']

    body = template('./templates/completion_email.tpl',
                    username=rec_name,
                    job_id=job_id,
                    url=url)

    st = sesconn.send_email(src_email,
                            "[JES] Your Job has completed",
                            body,
                            [rec_email])
    print st
    return st

##################################################################
# Send condolences for job failure
##################################################################
def send_failure_mail(data, app):
    sesconn     =  app.config['ses.conn']
    job_id      =  data.get('job_id')
    rec_email   =  data.get('user_email')
    rec_name    =  data.get('friendly_name') #data.get('username')
    src_email   =  app.config['ses.email_sender']
    url         =  app.config['server.url']

    body = template('./templates/failure_email.tpl',
                    username=rec_name,
                    job_id=job_id,
                    url=url)

    st = sesconn.send_email(src_email,
                            "[JES] Your Job has failed",
                            body,
                            [rec_email])
    print st
    return st


def init(app):

    ec2  = boto.ec2.connect_to_region(app.config["identity"]['region'],
                                      aws_access_key_id=app.config['keys.key_id'],
                                      aws_secret_access_key=app.config['keys.key_secret'],
                                      security_token=app.config['keys.key_token'])

    # Get meta tags
    meta_tags = {}
    for tag in ec2.get_all_tags():
        meta_tags[str(tag.name)] = str(tag.value)

    # Log the metadata tags
    app.config["instance.tags"] = meta_tags
    for k in meta_tags:
        logging.debug("[TAGS] {0} : {1}".format(k, meta_tags[k]))

    sqs  = boto.sqs.connect_to_region(app.config["identity"]['region'],
                                      aws_access_key_id=app.config['keys.key_id'],
                                      aws_secret_access_key=app.config['keys.key_secret'],
                                      security_token=app.config['keys.key_token'])

    sns  = boto.sns.connect_to_region(app.config["identity"]['region'],
                                      aws_access_key_id=app.config['keys.key_id'],
                                      aws_secret_access_key=app.config['keys.key_secret'],
                                      security_token=app.config['keys.key_token'])

    ses  = boto.ses.connect_to_region(app.config["identity"]['region'],
                                      aws_access_key_id=app.config['keys.key_id'],
                                      aws_secret_access_key=app.config['keys.key_secret'],
                                      security_token=app.config['keys.key_token'])

    s3   = S3Connection(aws_access_key_id=app.config['keys.key_id'],
                        aws_secret_access_key=app.config['keys.key_secret'],
                        security_token=app.config['keys.key_token'])

    dyno = Table(app.config["instance.tags"]["DynamoDBTableName"],#app.config['dynamodb.table_name'],                 
                 schema=[HashKey("job_id")],
                 connection=ddb.connect_to_region(app.config['dynamodb.region'],
                                                  aws_access_key_id=app.config['keys.key_id'],
                                                  aws_secret_access_key=app.config['keys.key_secret'],
                                                  security_token=app.config['keys.key_token']))

    app.config["ec2.conn"]  = ec2
    app.config["sns.conn"]  = sns
    app.config["sqs.conn"]  = sqs
    app.config["ses.conn"]  = ses
    app.config["s3.conn"]   = s3
    app.config["dyno.conn"] = dyno
    app.config["doReload"]  = True

    return app


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

    dyno = Table(app.config["instance.tags"]["DynamoDBTableName"], #app.config['dynamodb.table_name'],
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
            print keys
            keyfile = app.config[keys].replace('\"', '')

            logging.debug("Keyfile : {0}".format(keyfile.replace('\"', '')))
            if not os.path.isfile(keyfile):
                print "Key file {0} missing!".format(keyfile)
                logging.error("Key file {0} missing!".format(keyfile))
                exit(-1)
            with open(keyfile, 'r') as kf:
                ks = kf.readlines()
                sp = ks[1].split(',')
                app.config[keys] = kf.read()
                app.config["keys.key_id"] = sp[1]
                app.config["keys.key_secret"] = sp[2]
                app.config["keys.key_token"] = ''
                #print "keys : ", app.config[keys]
    if 'metadata.credurl' in app.config:
        update_creds_from_metadata_server(app)

    init(app)
    return app
