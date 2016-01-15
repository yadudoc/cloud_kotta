#!/usr/bin/env python
# Ref: http://bottlepy.org/docs/dev/tutorial.html

import uuid
import time, datetime
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
from datetime import datetime

import boto
import boto.ec2
from boto.s3.connection import S3Connection
import boto.dynamodb2 as ddb
from boto.dynamodb2.fields import HashKey
from boto.dynamodb2.table import Table

import bottle
from bottle import template
from bottle import route, get, post, request
from bottle import response, static_file
from bottle import app, SimpleTemplate, run

import s3_utils as s3
import sns_sqs
import dynamo_utils as dutils
import config_manager as conf_man

JobTypes = ["doc_to_vec", "generic", "experimental"]

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

##################################################################################
# This is only a dummy function for get_url to generate a dynamic route
##################################################################################
@route('/submit', method='GET', name="submit")
def url_maker_submit_job():    
    return template("./views/error.tpl",
                error_str="{0} is not a valid Job Type")    

##################################################################################
# Handles the different job types.
##################################################################################
@route('/submit/<jobtype>', method='GET', name="submit_job")
def submit_job(jobtype):
    if jobtype in JobTypes :
        t = template("./views/submit_{0}.tpl".format(jobtype),
                     email="",
                     username="",
                     jobtype=jobtype)

    else:
        t = template("./views/error.tpl",
                     error_str="{0} is not a valid Job Type",
                     email="",
                     username="")
 
    return t

@route('/submit_task', method='POST', name="submit_task")
def submit_job():
    conf_man.update_creds_from_metadata_server(app)
    username  = request.POST.get('username').strip()
    email     = request.POST.get('email').strip()
    input_url = request.POST.get('input_url')
    jobtype   = request.POST.get('jobtype').strip()
    executable= request.POST.get('executable')
    args      = request.POST.get('args')

    uid = str(uuid.uuid1())

    if jobtype == "doc_to_vec":        
        data = {"job_id"           : uid,
                "username"         : username,
                "user_email"       : email,
                "jobtype"          : "doc_to_vec",
                "inputs"           : [{"src": input_url, "dest": input_url.split('/')[-1] }],
                "outputs"          : [{"src": "doc_mat.pkl",  "dest": "klab-jobs/outputs/{0}/doc_mat.pkl".format(uid)},
                                      {"src": "word_mat.pkl", "dest": "klab-jobs/outputs/{0}/word_mat.pkl".format(uid)},
                                      {"src": "mdl.pkl",      "dest": "klab-jobs/outputs/{0}/mdl.pkl".format(uid)}],
                "submit_time"      : int(time.time()),
                "submit_stamp"     : str(time.strftime('%Y-%m-%d %H:%M:%S')),
                "status"           : "pending"
            }

    elif jobtype == "generic":
        data = {"job_id"           : uid,
                "username"         : username,
                "user_email"       : email,
                "jobtype"          : "bash_executor",
                "inputs"           : [],
                "outputs"          : [],
                "submit_time"      : int(time.time()),
                "submit_stamp"     : str(time.strftime('%Y-%m-%d %H:%M:%S')),
                "status"           : "pending"
            }

        for k in request.POST.keys():
            if k.startswith('input_url'):
                input_url =  request.POST.get(k)
                data["inputs"].extend([{"src" : input_url, 
                                        "dest": input_url.split('/')[-1]}])
            elif k.startswith('output_file'):
                output_file = request.POST.get(k)
                data["outputs"].extend([{"src" : output_file, 
                                         "dest": "klab-jobs/outputs/{0}/{1}".format(uid, output_file)}])
        print data
        

    dutils.dynamodb_update(app.config["dyno.conn"], data)
    sns_sqs.publish(app.config["sns.conn"], app.config["instance.tags"]["JobsSNSTopicARN"],
                    json.dumps(data))

    return template("./views/submit_confirm.tpl",
                    job_id=uid,
                    title="Task Confirmation")


#################################################################
# Print a table form of jobs and statuses
#################################################################
@route('/jobs', method='GET', name="jobs")
def list_jobs():
    conf_man.update_creds_from_metadata_server(app)
    results = app.config["dyno.conn"].scan()
    table_tpl = []

    print "Jobs: "
    print "-"*50
    for r in results:
        row = [str(r["job_id"]), str(r["status"]), 
               str(r["submit_stamp"]), str(r["username"])]
        table_tpl.append(row)

    table = sorted(table_tpl, key=lambda row: datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S'))
    return template("./views/jobs.tpl",
                    title="Task Status",
                    table=table)

    #return template(request.app.config['web.templates'] + "/home.tpl")


#################################################################
# Generate signed url
#################################################################
def generate_signed_url(key_path, app):
    URL="https://s3.amazonaws.com/{0}".format(key_path)
    S3_KEY=key_path
    
    exp_time  = int(time.time()) + 600
    h         = hmac.new(app.config['keys.key_secret'],
                         "GET\n\n\n{0}\n/{1}".format(exp_time,S3_KEY),
                         sha)
    
    signature = urllib.quote_plus(base64.encodestring(h.digest()).strip())
    #print signature
    return "{0}?AWSAccessKeyId={1}&Expires={2}&Signature={3}".format(URL,
                                                                     app.config['keys.key_id'],
                                                                     exp_time,
                                                                     signature);

@route('/jobs/<job_id>', method='GET', name="job_info")
def job_info(job_id):
    conf_man.update_creds_from_metadata_server(app)
    dyntable = app.config['dyno.conn']
    try:
        item = dyntable.get_item(job_id=job_id)
    except ItemNotFound:
        return "The requested job_id was not found in the jobs database"

    pairs = []
    for k in item.keys():
        print "{0} : {1}".format(k, item[k])
        if k.startswith("i_") :
            continue
        
        if k in ['submit_time', 'complete_time']:
            pairs.append([k, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item[k]))])
        
        elif k in ['inputs']:
            link       = '<a href="{0}">{1}</a>'.format(item[k][0]['src'], 
                                                        item[k][0]['dest'])
            print link
            pairs.append([k, link])
            
        elif k in ['outputs']:
            for out in item[k]:
                print "output ", out
                #signed_url = generate_signed_url(out["dest"], request.app)
                target = out["dest"].split('/', 1)
                signed_url = s3.generate_signed_url(request.app.config["s3.conn"],
                                                    target[0], # Bucket name
                                                    target[1], # Prefix
                                                    1500)      # Duration
                if signed_url :
                    link       = '<a href="{0}">{1}</a>'.format(signed_url, out["src"])
                else:
                    link       = "<i>{0}</i>".format(out["src"])

                pairs.append([k, link])
                        
        else:
            pairs.append([k, item[k]])

    print pairs
    return template('./views/job_info',
                    title="Job",
                    table= pairs, # Body
                    s3_inputs_bucket="https://s3.amazonaws.com/gas-inputs",
                    s3_results_bucket="https://s3.amazonaws.com",
                    log_path="/job_log")


    
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

   run(host='0.0.0.0', port=80, reloader=True, debug=True)
