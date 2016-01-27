#!/usr/bin/env python
# Ref: http://bottlepy.org/docs/dev/tutorial.html

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
from bottle import route, get, post, request
from bottle import response, static_file
from bottle import app, SimpleTemplate, run
from beaker.middleware import SessionMiddleware
import cherrypy

# My libraries
import s3_utils as s3
import sns_sqs
import dynamo_utils as dutils
import config_manager as conf_man
import identity

JobTypes = ["doc_to_vec", "generic", "experimental"]

##################################################################
# This function handles the creation of the encoded signature
# and policy.
##################################################################
def get_signature_and_policy(app, vals):
    private_key = app.config["instance.tags"]["S3UploadKeySecret"]
    input = ''

    with open("./views/policy.txt") as form_file:
        input = template(form_file.read(), vals)

    policy = input
    #print policy
    policy_encoded = base64.b64encode(policy)
    signature = base64.b64encode(hmac.new(private_key, policy_encoded, sha).digest())
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
                "executable"       : executable,
                "args"             : args,
                "user_email"       : email,
                "jobtype"          : "generic",
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
                print "Outfile : ", output_file
                data["outputs"].extend([{"src" : output_file, 
                                         "dest": "klab-jobs/outputs/{0}/{1}".format(uid, output_file)}])
        print "*" * 50
        print data
        print "*" * 50
        

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

    table = sorted(table_tpl, key=lambda row: datetime.datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S'), reverse=True)
    return template("./views/jobs.tpl",
                    title="Task Status",
                    table=table)

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


###################################################################
# Generate an expiry time that is N mins ahead of current timestamp
###################################################################
def tstamp_plus_nmins(mins):
    time = datetime.datetime.now(pytz.timezone('GMT')) + datetime.timedelta(minutes=mins)
    return time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
 

##################################################################
# GET request should get a form to the user
# A button which would POST a request to upload a file directly
# to S3
##################################################################
@get('/upload_confirm')
def upload_to_s3():
    return template("./views/upload_confirm.tpl",
                    job_id="foo",
                    title="Turing - Upload Success!")

   
##################################################################
# GET request should get a form to the user
# A button which would POST a request to upload a file directly
# to S3
##################################################################
@get('/upload')
def upload_to_s3():
    conf_man.update_creds_from_metadata_server(app)
    job_id   = str(uuid.uuid1())
    exp_time = tstamp_plus_nmins(60)

    vals = { "redirect_url" : "http://{0}:{1}/{2}".format(app.config["server.url"],
                                                          app.config["server.port"],
                                                          "upload_confirm"),
             "aws_key_id"   : app.config["instance.tags"]["S3UploadKeyId"],
             "job_id"       : job_id,
             "exp_date"     : exp_time,
             "bucket_name"  : "klab-webofscience"
         }

    policy, signature = get_signature_and_policy(app, vals)
    
    vals["policy"]    = policy
    vals["signature"] = signature

    return template('./views/upload.tpl',
                    name            = "",
                    email           = "", 
                    username        = "",
                    redirect_url    = vals["redirect_url"],
                    title           = "Analyze",
                    aws_key_id      = vals["aws_key_id"],
                    exp_date        = vals["exp_date"],
                    job_id          = vals["job_id"],
                    bucket_name     = vals["bucket_name"],
                    policy          = policy,
                    signature       = signature,
                    alert=False)


##################################################################
# GET request should get a form to the user
# A button which would POST a request to upload a file directly
# to S3
##################################################################
@get('/login')
def login():
    conf_man.update_creds_from_metadata_server(app)
    job_id   = str(uuid.uuid1())
    exp_time = tstamp_plus_nmins(60)
    return template('./views/login.tpl',
                    aws_client_id   = app.config["server.aws_client_id"],
                    username        = "",
                    alert=False)


##################################################################
# GET request should get a form to the user
# A button which would POST a request to upload a file directly
# to S3
##################################################################
@get('/handle_login')
def handle_login():
    conf_man.update_creds_from_metadata_server(app)
    access_token  = request.params.get("access_token")
    expires_in    = request.params.get("expires_in")
    aws_client_id = app.config["server.aws_client_id"]
    name, email, user_id = identity.get_identity_from_token(access_token, aws_client_id);

    return template("./views/login_confirm.tpl",
                    userid = user_id,
                    email  = email,
                    username = name,
                    title="Turing - Login Success!")



##################################################################
# HW5
# Update job information in dynamodb
##################################################################
def dynamodb_update(table, data):
    table.put_item(data=data, overwrite=True)
    return True

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

   session_options = {'session.type': 'cookie',
                      'session.cookie_expires': True,
                      'session.timeout': app.config['server.session.timeout'],
                      'session.httponly': True}

   SimpleTemplate.defaults['get_url'] = app.get_url


   run(host='0.0.0.0', port=int(app.config["server.port"]), reloader=True, debug=True, server='cherrypy')
