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
import identity

JobTypes = ["doc_to_vec", "generic", "experimental", "script"]

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

##################################################################
# Update job information in dynamodb
##################################################################
def dynamodb_update(table, data):
    table.put_item(data=data, overwrite=True)
    return True


###################################################################
# Generate an expiry time that is N mins ahead of current timestamp
###################################################################
def tstamp_plus_nmins(mins):
    return datetime.datetime.fromtimestamp(time.time()+(60*mins)).strftime('%Y%m%d%H%M%SZ')

###################################################################
# route to serve static content to internal pages
###################################################################
@route('/static/<filename:path>', method='GET', name="static")
def serve_static(filename):
    # Tell Bottle where static files should be served from
    return static_file(filename, root="static/")
    #return static_file(filename, root=request.app.config['web.static_root'])

###################################################################
# Home!
###################################################################
@route('/', method='GET', name="home")
def home_page():
    session = bottle.request.environ.get('beaker.session')
    print session
    #print request.app
    print "Home Page"
    return template("./views/home.tpl",
                    session=session)

##################################################################################
# This is only a dummy function for get_url to generate a dynamic route
##################################################################################
@route('/submit', method='GET', name="submit")
def url_maker_submit_job():    
    session = bottle.request.environ.get('beaker.session')
    return template("./views/error.tpl",
                    session=session,
                    error_str="{0} is not a valid Job Type")    
##################################################################################
# Helper function to ensure that the user is logged in
##################################################################################
def require_login(session):
    if not session:
        redirect("/login")
    if session.get("logged_in") != True:
        redirect("/login")

##################################################################################
# Handles the different job types.
##################################################################################
@route('/submit/<jobtype>', method='GET', name="submit_job")
def submit_job(jobtype):
    session = bottle.request.environ.get('beaker.session')
    require_login(session)
    if jobtype in JobTypes :
        t = template("./views/submit_{0}.tpl".format(jobtype),
                     email="",
                     username="",
                     jobtype=jobtype,
                     session=session)

    else:
        t = template("./views/error.tpl",
                     error_str="{0} is not a valid Job Type",
                     email="",
                     username="",
                     session=session)
                    
    return t


##################################################################################
# Submit tasks
##################################################################################
@route('/submit_task', method='POST', name="submit_task")
def submit_job_description():
    session = bottle.request.environ.get('beaker.session')
    conf_man.update_creds_from_metadata_server(request.app)
    # Fixing naming issue with names in forms
    user_id   = request.POST.get('username').strip() # Username in the form is the user_id
    email     = request.POST.get('email').strip()
    input_url = request.POST.get('input_url')
    jobtype   = request.POST.get('jobtype').strip()
    executable= request.POST.get('executable')
    args      = request.POST.get('args', '')
    walltime  = request.POST.get('walltime')
    walltime  = int(walltime) * 60;
    queue     = request.POST.get('queue')
    username  = session["username"]
    role      = session["user_role"]
    outputs   = request.POST.get('outputs', None)
    uid = str(uuid.uuid1())

    if jobtype == "doc_to_vec":
        data = {"job_id"           : uid,
                "username"         : username,
                "i_user_id"        : user_id,
                "i_user_role"      : role,
                "user_email"       : email,
                "jobtype"          : "doc_to_vec",
                "inputs"           : [{"type": "doc", "src": input_url, "dest": input_url.split('/')[-1] }],
                "outputs"          : [{"src": "doc_mat.pkl",  "dest": "klab-jobs/outputs/{0}/doc_mat.pkl".format(uid)},
                                      {"src": "word_mat.pkl", "dest": "klab-jobs/outputs/{0}/word_mat.pkl".format(uid)},
                                      {"src": "mdl.pkl",      "dest": "klab-jobs/outputs/{0}/mdl.pkl".format(uid)},
                                      {"src": "STDOUT.txt",   "dest": "klab-jobs/outputs/{0}/STDOUT.txt".format(uid)},
                                      {"src": "STDERR.txt",   "dest": "klab-jobs/outputs/{0}/STDERR.txt".format(uid)},
                                      {"src": "pipeline.log", "dest": "klab-jobs/outputs/{0}/pipeline.log".format(uid)}],
                "submit_time"      : int(time.time()),
                "submit_stamp"     : str(time.strftime('%Y-%m-%d %H:%M:%S')),
                "walltime"         : walltime,
                "queue"            : queue,
                "status"           : "pending"
                
            }
        model_url = request.POST.get('model_url')
        if model_url :
            print "Model url : {0}".format(model_url)
            data["inputs"].extend([{"type": "model", "src": model_url, "dest": model_url.split('/')[-1]}])
            print data["inputs"]
        else:
            print "Model URL not present"

        params_url = request.POST.get('params_url')
        if params_url :
            print "Params url : {0}".format(params_url)
            data["inputs"].extend([{"type": "params", "src": params_url, "dest": params_url.split('/')[-1]}])
            print data["inputs"]
        else:
            print "Params URL not present"


    elif jobtype == "script":
        print "--" * 40

        script = request.POST.get('script').rstrip('\r')
        script_name = request.POST.get('script_name')

        data = {"job_id"           : uid,
                "username"         : username,
                "i_user_id"        : user_id,
                "i_user_role"      : role,
                "user_email"       : email,
                "executable"       : executable,
                "args"             : args,                
                "i_script"         : script,
                "i_script_name"    : script_name,
                "jobtype"          : "script",
                "submit_time"      : int(time.time()),
                "submit_stamp"     : str(time.strftime('%Y-%m-%d %H:%M:%S')),
                "queue"            : queue,
                "outputs"          : [],
                "inputs"           : [],
                "walltime"         : walltime,
                "status"           : "pending"
            }

        data["outputs"].extend([{"src" : script_name, 
                                 "dest": "klab-jobs/outputs/{0}/{1}".format(uid, script_name)}])
        
        for k in request.POST.keys():
            print "Key : {0}".format(k)
            if k.startswith('input_url'):
                input_url =  request.POST.get(k)
                data["inputs"].extend([{"src" : input_url, 
                                        "dest": input_url.split('/')[-1]}])
            elif k == "inputs" :
                inputs = request.POST.get(k)
                if inputs :
                    inp = [{"src":x.strip(), "dest":x.strip().split('/')[-1]} for x in inputs.split(',')]
                    data["inputs"].extend(inp)
                
            elif k == "outputs":
                if not outputs :
                    continue
                for outfile in outputs.split(','):
                    outfile = outfile.lstrip().rstrip()                    
                    data["outputs"].extend([{"src" : outfile, 
                                             "dest": "klab-jobs/outputs/{0}/{1}".format(uid, outfile)}])

            elif k.startswith('output_'):
                output_file = request.POST.get(k)
                print "Outfile : ", output_file
                data["outputs"].extend([{"src" : output_file, 
                                         "dest": "klab-jobs/outputs/{0}/{1}".format(uid, output_file)}])

        print "*" * 50
        for k in data:
            #print k
            print "{0:20} | {1:20}".format(k, data.get(k))
        print "--" * 40
        

    elif jobtype == "generic":
             
        data = {"job_id"           : uid,
                "username"         : username,
                "i_user_id"        : user_id,
                "i_user_role"      : role,
                "executable"       : executable,
                "args"             : args,
                "user_email"       : email,
                "jobtype"          : "generic",
                "inputs"           : [],
                "outputs"          : [],
                "submit_time"      : int(time.time()),
                "submit_stamp"     : str(time.strftime('%Y-%m-%d %H:%M:%S')),
                "queue"            : queue,
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
       
    enable_mock = False

    if enable_mock :
        return template("./views/submit_confirm.tpl",
                        job_id="MOCK-{0}".format(uid),
                        title="Task Confirmation - MOCK",
                        session=session)


    dutils.dynamodb_update(request.app.config["dyno.conn"], data)
    qname = "TestJobsSNSTopicARN"
    if queue in ["Test", "Prod"]:
        qname = queue + "JobsSNSTopicARN"
            
    sns_sqs.publish(request.app.config["sns.conn"], request.app.config["instance.tags"][qname],
                    json.dumps(data))

    return template("./views/submit_confirm.tpl",
                    job_id=uid,
                    title="Task Confirmation",
                    session=session)
            
#################################################################
# Print a table form of jobs and statuses
#################################################################
@route('/jobs', method='GET', name="jobs")
def list_jobs():

    session = bottle.request.environ.get('beaker.session')
    require_login(session)
    current_user = session["user_id"]

    conf_man.update_creds_from_metadata_server(request.app)
    results = request.app.config["dyno.conn"].scan(i_user_id__eq=current_user)
    table_tpl = []

    print "Jobs: "
    print "-"*50
    for r in results:
        row = [str(r["job_id"]), str(r["status"]),  
               str(r["jobtype"]), str(r["submit_stamp"])]
        table_tpl.append(row)

    table = sorted(table_tpl, key=lambda row: datetime.datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S'), reverse=True)
    return template("./views/jobs.tpl",
                    title="Task Status",
                    table=table,
                    session=session)
            

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

@route('/cancel', method='GET', name="job_cancel")
def cancel(job_id):
    return

#################################################################
# Cancel a job
#################################################################
@route('/cancel/<job_id>', method='GET', name="cancel")
def job_cancel(job_id):
    
    session = bottle.request.environ.get('beaker.session')
    require_login(session)

    conf_man.update_creds_from_metadata_server(request.app)
    dyntable = request.app.config['dyno.conn']

    try:
        tstamp = str(time.strftime('%Y-%m-%d %H:%M:%S'))
        item = dyntable.get_item(job_id=job_id)
        item["status"] = "cancelled"
        item["reason"] =  "User request cancel"
        item["cancel_time"] = tstamp
        dynamodb_update(dyntable, item)

    except ItemNotFound:
        return "The requested job_id was not found in the jobs database"

    redirect('/jobs/' + job_id)

@route('/jobs/<job_id>', method='GET', name="job_info")
def job_info(job_id):
    
    session = bottle.request.environ.get('beaker.session')
    require_login(session)

    conf_man.update_creds_from_metadata_server(request.app)
    dyntable = request.app.config['dyno.conn']
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
            if item["status"].lower() not in ["completed", "failed"]:
                continue

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
                    title="Job - Info",
                    job_id=job_id,
                    table= pairs, # Body
                    log_path="/job_log",
                    session=session)


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
@get('/browse', method='GET', name="browse")
def browse_folders():
    session = bottle.request.environ.get('beaker.session')
    list_buckets = ["klab-webofscience", "klab-jobs"]

    
    return template("./views/upload_confirm.tpl",
                    job_id="foo",
                    title="Turing - Upload Success!",
                    session=session)


##################################################################
# GET request should get a form to the user
# A button which would POST a request to upload a file directly
# to S3
##################################################################
@get('/upload_confirm')
def upload_to_s3():
    session = bottle.request.environ.get('beaker.session')
    
    bucket  =  request.params.get('bucket')
    key     =  request.params.get('key')
    etag    =  request.params.get('etag')
    signed_url = s3.generate_signed_url(request.app.config["s3.conn"],
                                        bucket,
                                        key,
                                        1500)   # Duration
    link = '<a href="{0}">{1}</a>'.format(signed_url,
                                          key.split('/')[-1])
    unsigned = "https://s3.amazonaws.com/{0}/{1}".format(bucket, key)
        
    #"klab-webofscience/uploads/amzn1.account.AEKWXVYINCBBNY5MPRMOYND6CWWA/Screenshot+from+2016-01-27+01%3A18%3A51.png"
    return template("./views/upload_confirm.tpl",
                    signed_url=link,
                    unsigned = unsigned,
                    job_id="foo",
                    title="Turing - Upload Success!",
                    session=session)

##################################################################
# GET request should get a form to the user
# A button which would POST a request to upload a file directly
# to S3
##################################################################
@get('/upload', method='GET', name="upload")
def upload_to_s3():
    session = bottle.request.environ.get('beaker.session')
    require_login(session)

    conf_man.update_creds_from_metadata_server(request.app)
    job_id   = str(uuid.uuid1())
    exp_time = tstamp_plus_nmins(60)
    bucket_name = "klab-webofscience" #"klab-jobs"

    vals = { "redirect_url" : "http://{0}:{1}/{2}".format(request.app.config["server.url"],
                                                          request.app.config["server.port"],
                                                          "upload_confirm"),
             "aws_key_id"   : request.app.config["instance.tags"]["S3UploadKeyId"],
             "job_id"       : job_id,
             "exp_date"     : exp_time,
             "bucket_name"  : bucket_name
         }

    policy, signature = get_signature_and_policy(request.app, vals)
    
    vals["policy"]    = policy
    vals["signature"] = signature

    return template('./views/upload.tpl',
                    name            = "",
                    email           = "", 
                    username        = "",
                    redirect_url    = vals["redirect_url"],
                    aws_key_id      = vals["aws_key_id"],
                    exp_date        = vals["exp_date"],
                    job_id          = vals["job_id"],
                    bucket_name     = vals["bucket_name"],
                    policy          = policy,
                    signature       = signature,
                    alert=False,
                    title="Upload data",
                    session=session)


@get('/logout', method='GET', name="logout")
def logout():
    session  = bottle.request.environ.get('beaker.session')
    require_login(session)
    
    username = session["username"]
    session["logged_in"] = False
    session["user_id"]   = None
    session["username"]  = None
    session["email"]     = None
    session.delete()

    return template('./views/logout.tpl',
                    username=username,
                    session=session,
                    title="Logging out",
                    alert=False)


##################################################################
# GET request should get a form to the user
# A button which would POST a request to upload a file directly
# to S3
##################################################################
@get('/login', method='GET', name="login")
def login():
    #conf_man.update_creds_from_metadata_server(request.app)
    session = bottle.request.environ.get('beaker.session')
    return template('./views/login.tpl',
                    aws_client_id   = request.app.config["server.aws_client_id"],
                    username        = "",
                    session=session,
                    alert=False)


##################################################################
# Handle the redirect from Login with Amazon.
# Retrieve user identity from Amazon with the temp access_token
# Use id to verify against valid users and get appropriate role.
# Get temporary keys for the role and post to session.
##################################################################
@get('/handle_login')
def handle_login():
    session = bottle.request.environ.get('beaker.session')
    conf_man.update_creds_from_metadata_server(request.app)
    access_token  = request.params.get("access_token")
    expires_in    = request.params.get("expires_in")
    aws_client_id = request.app.config["server.aws_client_id"]
    user_id, name, email = identity.get_identity_from_token(access_token, aws_client_id);
    user_info = identity.find_user_role(request.app, user_id)

    
    if not user_info :
        return template("./views/login_reject.tpl",
                        title="Turing - Login Rejected!",
                        username = name,
                        user_id  = user_id,                    
                        email    = email,
                        session  = session)

    
    session["logged_in"] = True
    session["user_id"]   = user_id
    session["username"]  = name
    session["email"]     = user_info["email"] #email
    session["user_role"] = user_info["role"]

    print session
    return template("./views/login_confirm.tpl",
                    title="Turing - Login Success!",
                    session=session)


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
                      'session.auto': True, # Saves the cookie automatically on update
                      'session.encrypt_key': app.config['server.session.encrypt_key'],
                      'session.validate_key': app.config['server.session.validate_key'],
                      'session.timeout': app.config['server.session.timeout']}
   #'session.httponly': True}

   app = SessionMiddleware(app, session_options)
   SimpleTemplate.defaults['get_url'] = app.wrap_app.get_url

   #SimpleTemplate.defaults['get_url'] = app.get_url

   run(app=app,
       host='0.0.0.0', 
       #port=int(app.config["server.port"]), 
       port=int(app.wrap_app.config["server.port"]), 
       reloader=True, 
       debug=True, 
       server='cherrypy')
