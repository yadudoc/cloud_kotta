#!/usr/bin/env python
# Ref: http://bottlepy.org/docs/dev/tutorial.html

import uuid
import time, datetime
import subprocess
import os
import glob
import json
import logging
import boto
import boto.ec2
import urllib2
from bottle import template
from boto.s3.connection import S3Connection
import boto.dynamodb2 as ddb
from boto.dynamodb2.fields import HashKey
from boto.dynamodb2.table import Table

from bottle import route, get, post, request
from bottle import response, static_file
from bottle import app, SimpleTemplate, run

import base64, hmac, sha
import s3_utils as s3
import sns_sqs
import argparse
import config_manager as conf_man
import bottle

##################################################################
# This function handles the creation of the encoded signature
# and policy.
##################################################################
def get_signature_and_policy(vals):
    private_key = str(configs['AWSSecretKey'])
    input = ''

    with open("policy.txt") as form_file:
        input = template(form_file.read(), vals)

    policy = input
    #print policy
    policy_encoded = base64.b64encode(policy)
    signature = base64.b64encode(hmac.new(private_key, policy_encoded, sha).digest())
    #print "Your policy base-64 encoded is %s." % (policy_encoded)
    #print "Your signature base-64 encoded is %s." % (signature)
    return (policy_encoded, signature)

###################################################################
# Generate an expiry time that is N mins ahead of current timestamp
###################################################################
def tstamp_plus_nmins(mins):
    return datetime.datetime.fromtimestamp(time.time()+(60*mins)).strftime('%Y%m%d%H%M%SZ')


@route('/static/<filename:path>', method='GET', name="static")
def serve_static(filename):
    # Tell Bottle where static files should be served from
    return static_file(filename, root="static/")
    return static_file(filename, root=request.app.config['web.static_root'])

@route('/', method='GET', name="home")
def home_page():
    print "Home Page"
    return template("./views/home.tpl")
    #return template(request.app.config['web.templates'] + "/home.tpl")

@route('/submit', method='GET', name="submit")
def submit_job():
    return template("./views/submit.tpl",
                    email="",
                    username="")

    #return template(request.app.config['web.templates'] + "/home.tpl")

@route('/submit_task', method='POST', name="submit_task")
def submit_job():

    username  = request.POST.get('username').strip()
    print "Name: ", username
    email     = request.POST.get('email').strip()
    print "Email: ", email
    input_url = request.POST.get('input_url').strip()
    print "Url : ", input_url

    print "Submit task received"
    return "Submit task received!"
    return template("./views/submit.tpl")
    #return template(request.app.config['web.templates'] + "/home.tpl")

@route('/tasks', method='GET', name="tasks")
def list_tasks():
    return template("./views/tasks.tpl")
    #return template(request.app.config['web.templates'] + "/home.tpl")

##################################################################
# GET request should get a form to the user
# A button which would POST a request to upload a file directly
# to S3
##################################################################
@get('/upload')
def get_submit():

    job_id   = str(uuid.uuid1())
    exp_time = tstamp_plus_nmins(10)
    vals = { "redirect_url" : "http://ec2-52-2-209-210.compute-1.amazonaws.com:8888/upload_done", # "http://ec2-52-0-35-15.compute-1.amazonaws.com:8888/annotator",
             "aws_key_id"   : configs['AWSAccessKeyId'],
             "job_id"       : job_id,
             "exp_date"     : exp_time, #"20151212T000000Z",
             "bucket_name"  : "gas-inputs"
         }

    policy, signature = get_signature_and_policy(vals)
    vals["policy"]    = policy
    vals["signature"] = signature

    form = ''
    with open("upload.tpl") as form_file:
        form = template(form_file.read(), vals)

    print form
    return form

##################################################################
# HW5
# Update job information in dynamodb
##################################################################
def dynamodb_update(table, data):
    table.put_item(data=data, overwrite=True)
    return True


annotator_url="http://52.2.101.61:8888/annotator"
topic_arn  = 'arn:aws:sns:us-east-1:127134666975:yadunand-job-notifications'
##################################################################
# HW5
# GET request should get a form to the user
# A button which would POST a request to upload a file directly
# to S3
##################################################################
@route('/upload_done', method='GET')
def upload_done():
    src_bucket  =  request.params.get('bucket')
    key         =  request.params.get('key')
    etag        =  request.params.get('etag')
    dest_bucket =  'gas-results'
    response.status = 400

    data = {"job_id"           : key.split('/')[-1],
            "username"         : s3.get_s3_meta(s3conn, src_bucket, key, 'username'),
            "s3_inputs_bucket" : src_bucket,
            "s3_key_input_file": key,
            "input_file_name"  : s3.get_s3_meta(s3conn, src_bucket, key, 'filename'),
            "submit_time"      : int(time.time()),
            "status"           : "pending"
        }

    dynamodb_update(dynotable,  data)

    print "Publishing : ", sns_sqs.publish(sns, topic_arn, data)

    ##################################################################
    #HW5 Part1
    '''
    url = annotator_url
    headers = {'Content-Type' : 'application/json'}
    ann_request = urllib2.Request(url, json.dumps(data), headers)
    annotator_response = urllib2.urlopen(ann_request)
    '''
    ##################################################################
    response.content_type = 'application/json'
    return data #annotator_response


if __name__ == "__main__":

   parser   = argparse.ArgumentParser()
   parser.add_argument("-v", "--verbose", default="DEBUG", help="set level of verbosity, DEBUG, INFO, WARN")
   parser.add_argument("-l", "--logfile", default="web_server.log", help="Logfile path. Defaults to ./web_server.log")
   parser.add_argument("-c", "--conffile", default="test.conf", help="Config file path. Defaults to ./test.conf")
   parser.add_argument("-j", "--jobid", type=str, action='append')
   parser.add_argument("-i", "--workload_id", default=None)
   args   = parser.parse_args()


   if args.verbose not in conf_man.log_levels :
      print "Unknown verbosity level : {0}".format(args.verbose)
      print "Cannot proceed. Exiting"
      exit(-1)

   logging.basicConfig(filename=args.logfile, level=conf_man.log_levels[args.verbose],
                       format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                       datefmt='%m-%d %H:%M')

   logging.debug("\n{0}\nStarting webserver\n{0}\n".format("*"*50))
   app = conf_man.load_configs(args.conffile);
   SimpleTemplate.defaults['get_url'] = app.get_url
   print app.config
   run(host='0.0.0.0', port=8888, reloader=True, debug=True)
