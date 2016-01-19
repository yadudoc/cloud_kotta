#!/usr/bin/env python

import logging
import uuid
import json
import boto
import boto.ec2

def _read_conf(config_file):
    cfile = open(config_file, 'r').read()
    config = {}
    for line in cfile.split('\n'):

        if line.startswith('#') or not line :
            continue

        temp = line.split('=')
        config[temp[0]] = temp[1].strip('\r')
    return config


def load_confs(conf_file):

    configs = _read_conf(conf_file)

    if not configs['AWS_CREDENTIALS_FILE']:
        print "No creds file found"
        exit(-1)

    creds = []
    with open(configs['AWS_CREDENTIALS_FILE']) as cred_file:
        creds = json.load(cred_file)

    configs['AWSAccessKeyId'] = creds['AccessKey']['AccessKeyId']
    configs['AWSSecretKey']   = creds['AccessKey']['SecretAccessKey']
    return configs

def init():
    configs    = load_confs("configs")

    regions    = boto.ec2.regions()

    logging.debug("AWS region : ", configs['AWS_REGION'])
    if configs['AWS_REGION'] not in [x.name for x in regions]:
        print configs['AWS_REGION']

    conn       = boto.ec2.connect_to_region(configs['AWS_REGION'],
                                            aws_access_key_id=configs['AWSAccessKeyId'],
                                            aws_secret_access_key=configs['AWSSecretKey'])
    if conn == None :
        print "[INFO] : Region name could be incorrect"
        print "[ERROR]: Failed to connect to region, exiting"
        exit(-1)

    return configs, conn
