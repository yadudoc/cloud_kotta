import uuid
import time, datetime, pytz
import subprocess
import os
import glob
import json
import logging
import argparse
import urllib2
import uuid
import base64, hmac, sha
import urllib
import sys
import utils
import ast
# Boto imports
import boto
import boto.ec2
from boto.s3.connection import S3Connection
import boto.dynamodb2 as ddb
from boto.dynamodb2.fields import HashKey
from boto.dynamodb2.table import Table

# Bottle and webframework imports
import bottle
from bottle import template
from bottle import route, get, post, request, hook, redirect
from bottle import response, static_file
from bottle import app, SimpleTemplate, run
from beaker.middleware import SessionMiddleware
import cherrypy

# My libraries
import s3_utils as s3
import sns_sqs
import dynamo_utils as dutils
import config_manager as conf_man
from utils import *
import web_server

##################################################################################
# This is only a dummy function for get_url to generate a dynamic route
##################################################################################
@route('/resubmit', method='GET', name="resubmit")
def url_maker_resubmit_job():    
    session = bottle.request.environ.get('beaker.session')
    return template("./views/error.tpl",
                    session=session,
                    error_str="You've requested an invalid Job Type")    

##################################################################################
# Handles the different job types.
##################################################################################
@route('/resubmit/<jobid>', method='GET', name="resubmit_job")
def re_submit_job(jobid):
    session = bottle.request.environ.get('beaker.session')
    require_login(session)
    print "In resubmit =============================="


    item = dutils.get_job(request, jobid)

    mapping = {}    
    for k in item.keys():
        v = item[k]
        print "{0} : {1}".format(k, v)

        if str(k) == 'outputs' or str(k) == 'inputs':
            mapping[k] = [o['src'] for o in v if o['src'] not in ['STDOUT.txt', 'STDERR.txt']]
            print "string : ", mapping[k]

        else:
            mapping[k] = v

    print "Before trimming : ", mapping['outputs']
    if mapping.get('i_script_name', None) != None:
        mapping['outputs'].remove(mapping.get('i_script_name'))
    print "After trimming : ", mapping['outputs']
    
    if mapping.get('outputs', None) is not None:
        mapping['outputs'] = ', '.join(mapping['outputs'])
    else:
        mapping['outputs'] = ''

    if mapping.get('inputs', None) is not None:
        mapping['inputs']  = ', '.join(mapping['inputs'])
    else:
        mapping['inputs'] = ''
    
    jobtype = mapping.get('jobtype', None)
    #print "inputs: ", mapping['inputs']
    #print "outputs: ", mapping['outputs']

    if jobtype in JobTypes :
        t = template("./views/submit_{0}.tpl".format(jobtype),
                     email="",
                     username="",
                     jobtype=jobtype,
                     prefill=mapping,
                     session=session)

    else:
        t = template("./views/error.tpl",
                     error_str="{0} is not a valid Job Type".format(jobtype),
                     email="",
                     username="",
                     session=session)
    return t

