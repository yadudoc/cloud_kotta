#!/usr/bin/env python
# Ref: http://bottlepy.org/docs/dev/tutorial.html
import uuid
import time, datetime, pytz
import subprocess
import os
import glob
import json
import csv
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
import identity
import sts
from utils import *
from usage_stats import *
from resubmit import *


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
                    error_str="You've requested an invalid Job Type")    

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
                     prefill=None,
                     jobtype=jobtype,
                     session=session)

    else:
        t = template("./views/error.tpl",
                     error_str="{0} is not a valid Job Type".format(jobtype),
                     email="",
                     username="",
                     session=session)                    
    return t


################################################################################
# Use the access_token to verify the user and get her account details
################################################################################
def validate_session(app ,access_token):
                    
    if not access_token:
        return None

    aws_client_id        = request.app.config["server.aws_client_id"]
    user_id, name, email = identity.get_identity_from_token(access_token, aws_client_id);
    if not user_id or not name:
        return None

    print "User_id : ", user_id
    print "Name    : ", name
    print "Email   : ", email
    user_info = identity.find_user_role(request.app, user_id)
    
    info = {"user_id"   : user_id,
            "name"      : name,
            "username"  : name,
            "email"     : user_info["email"], #email
            "user_role" : user_info["role"] }

    return info

def _submit_task(request, session):

    user_id   = session["user_id"]
    input_url = request.POST.get('input_url')
    jobtype   = request.POST.get('jobtype').strip()
    outputs   = request.POST.get('outputs', None)
    uid       = str(uuid.uuid4())
    queue     = request.POST.get('queue')

    data      = {"job_id"           : uid,
                 "username"         : session["username"],
                 "i_user_id"        : session["user_id"],
                 "jobname"          : request.POST.get('jobname', uid),
                 "i_user_role"      : "arn:aws:iam::{0}:role/{1}".format(request.app.config["iam.project"], session["user_role"]),
                 "user_email"       : session["email"],
                 "submit_time"      : int(time.time()),
                 "submit_stamp"     : str(time.strftime('%Y-%m-%d %H:%M:%S')),
                 "walltime"         : int(request.POST.get('walltime')) * 60,
                 "queue"            : queue,
                 "jobtype"          : jobtype,
                 "status"           : "pending"                
            }
    
    ##############################################################################################################
    # Doc_to_vec specific attributes
    ##############################################################################################################
    if jobtype == "doc_to_vec":

        print "Inputs : ", [{"type": "doc", "src": input_url, "dest": input_url.split('/')[-1] }]

        data["inputs"]   =  [{"type": "doc", "src": input_url, "dest": input_url.split('/')[-1] }]
        data["outputs"]  =  [{"src": "doc_mat.pkl",  "dest": "klab-jobs/outputs/{0}/doc_mat.pkl".format(uid)},
                             {"src": "word_mat.pkl", "dest": "klab-jobs/outputs/{0}/word_mat.pkl".format(uid)},
                             {"src": "mdl.pkl",      "dest": "klab-jobs/outputs/{0}/mdl.pkl".format(uid)},
                             {"src": "STDOUT.txt",   "dest": "klab-jobs/outputs/{0}/STDOUT.txt".format(uid)},
                             {"src": "STDERR.txt",   "dest": "klab-jobs/outputs/{0}/STDERR.txt".format(uid)},
                             {"src": "pipeline.log", "dest": "klab-jobs/outputs/{0}/pipeline.log".format(uid)}]

        model_url = request.POST.get('model_url')
        if model_url :
            data["inputs"].extend([{"type": "model", "src": model_url, "dest": model_url.split('/')[-1]}])

        params_url = request.POST.get('params_url')
        if params_url :
            data["inputs"].extend([{"type": "params", "src": params_url, "dest": params_url.split('/')[-1]}])

    elif jobtype == "script":

        data["executable"]    = request.POST.get('executable')
        data["args"]          = request.POST.get('args', '')
        data["i_script"]      = request.POST.get('script').rstrip('\r')
        data["i_script_name"] = request.POST.get('script_name')
        data["outputs"]       = []
        data["inputs"]        = []

        data["outputs"].extend([{"src" : data["i_script_name"], 
                                 "dest": "klab-jobs/outputs/{0}/{1}".format(uid, data["i_script_name"])}])
        
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
            print "{0:20} | {1:20}".format(k, data.get(k))
        print "--" * 40
        
       
    enable_mock = False
    #enable_mock = True

    if enable_mock :
        return template("./views/submit_confirm.tpl",
                        job_id="MOCK-{0}".format(uid),
                        title="Task Confirmation - MOCK",
                        session=session)


    dutils.dynamodb_update(request.app.config["dyno.conn"], data)
    qname = "TestJobsSNSTopicARN"
    if queue in ["Test", "Prod"]:
        qname = queue + "JobsSNSTopicARN"
    else:
        raise Exception("Queue : [{0}] is not valid".format(queue))

    sns_sqs.publish(request.app.config["sns.conn"], request.app.config["instance.tags"][qname],
                    json.dumps(data))

    return uid


##################################################################################
# Submit tasks via REST
##################################################################################
@route('/rest/v1/submit_task', method='POST', name="submit_task_rest")
def submit_job_description():
    print "Rest Interface for submit_task"
    session = bottle.request.environ.get('beaker.session')
    response.content_type = 'application/json'
    
    if request.POST.get("access_token"):
        print "Attempt to auth with access_token"
        user_info = validate_session(request.app, request.POST.get("access_token"))
        if not user_info :
            return {"status" : "Fail",
                    "reason" : "Failed to authenticate"}

        session.update(user_info)
        session["logged_in"] = True
        #print "Session : ",session
    else:        
        return {"status" : "Fail",
                "reason" : "access_token missing"}
    try:
        uid = _submit_task(request, session)
    except Exception as e:
        return {"status" : "Fail",
                "reason" : "{0}".format(e)}
        
    return {"status" : "Success", 
            "job_id" : uid} 


##################################################################################
# Submit tasks
##################################################################################
@route('/submit_task', method='POST', name="submit_task")
def submit_job_description():
    session = bottle.request.environ.get('beaker.session')
    conf_man.update_creds_from_metadata_server(request.app)

    uid = _submit_task(request, session)

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
        jobinfourl = request.app.get_url('/jobs')+"/"+str(r["job_id"])
        joburl     = ''
        if r["jobname"] :
            joburl = '<a href="{0}">{1}</a>'.format(jobinfourl, r["jobname"])
        else:
            joburl = '<a href="{0}">{1}</a>'.format(jobinfourl, str(r["job_id"]))
                                                
        row = [joburl , str(r["status"]),  
               str(r["jobtype"]), str(r["submit_stamp"])]
        table_tpl.append(row)

    table = sorted(table_tpl, key=lambda row: datetime.datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S'), reverse=True)
    return template("./views/jobs.tpl",
                    title="Task Status",
                    table=table,
                    session=session)

#################################################################
# Print a table form of jobs and statuses
#################################################################
@route('/rest/v1/list_tasks', method='GET', name="jobs_list_rest")
def list_jobs_rest():
    print "Rest Interface for list_task"
    session = bottle.request.environ.get('beaker.session')
    response.content_type = 'application/json'
    
    if request.POST.get("access_token"):
        print "Attempt to auth with access_token"
        user_info = validate_session(request.app, request.POST.get("access_token"))
        if not user_info :
            return {"status" : "Fail",
                    "reason" : "Failed to authenticate"}

        session.update(user_info)
        session["logged_in"] = True
        #print "Session : ",session
    else:        
        return {"status" : "Fail",
                "reason" : "access_token missing"}

    
    conf_man.update_creds_from_metadata_server(request.app)
    results = request.app.config["dyno.conn"].scan(i_user_id__eq=session['user_id'])
    table_tpl = {}

    table_tpl['items'] = {}
    print "Jobs: "
    print "-"*50
    for i,r in enumerate(results):
        table_tpl['items'][i] = { "job_id"       : str(r["job_id"]),
                                  "status"       : str(r["status"]),
                                  "jobtype"      : str(r["jobtype"]),
                                  "submit_stamp" : str(r["submit_stamp"])}

    table_tpl['status'] = "Success"
    return table_tpl
            

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

def get_job_info(request, job_id):

    item = dutils.get_job(request, job_id)
    pairs = []
    for k in item.keys():

        if k.startswith("i_") :
            continue
        
        if k in ['submit_time', 'complete_time', 'start_time']:            
            pairs.append([k, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item[k]))])
        
        elif k in ['inputs']:
            link       = '<a href="{0}">{1}</a>'.format(item[k][0]['src'], 
                                                        item[k][0]['dest'])
            pairs.append([k, link])
            
        elif k in ['outputs']:
            if item["status"].lower() not in ["completed", "failed"]:
                continue

            for out in item[k]:
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

    return pairs

#################################################################
# Show job attributes
#################################################################
@route('/rest/v1/status_task/<job_id>', method='GET', name="job_info")
def job_info(job_id):
    
    session = bottle.request.environ.get('beaker.session')
    conf_man.update_creds_from_metadata_server(request.app)
    response.content_type = 'application/json'

    pairs = get_job_info(request, job_id)
    result = {}
    result['items'] = {}
    print "Pairs : ", pairs
    for i,p in enumerate(pairs):
        result['items'][i] = {p[0]:p[1]}
        if p[0] == "status":
            result['status'] = p[1]
    #print result
    return result
    #return json.dumps(pairs)

def human_time(seconds):
    m, s  = divmod(seconds, 60)
    h, m  = divmod(m, 60)
    return "{0:02d}:{1:02d}:{2:02d}".format(h, m, s)


def extract_usage_stats(data, fname):
    key  = 'usage_stats'
    if not data:
        return "None"
        
    data = '[' + data.replace('}{', '},{') + ']'
    ddata = ast.literal_eval(data)
    with open(fname, 'w') as csvfile:
        fieldnames = ['time', 'cpu', 'memmax', 'memcur']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in ddata[::int(math.floor(len(ddata)/100)+1)]:
            writer.writerow({'time': str(time.strftime('%H:%M:%S', time.localtime(float(row['time'])))),
                             #'time': "foo", #row['time'], 
                             'cpu' : row['cpu'].split(', ')[0],
                             'memmax' : row['mem'].split(', ')[0],
                             'memcur' : row['mem'].split(', ')[1],
                         })
        
    return fname


# TODO: Remove duplication of work with get_job_info
#################################################################
# Show job attributes
#################################################################
@route('/jobs/<job_id>', method='GET', name="job_info")
def job_info(job_id):
    
    session = bottle.request.environ.get('beaker.session')
    require_login(session)

    pairs = get_job_info(request, job_id);
    tdata, cdata, mmax, mcur = None, None, None, None
    fname = "None"
    for row in pairs:
        # The walltime is in seconds, convert this to some human readable form
        if row[0] == 'walltime':
            row[1] = human_time(int(row[1]))
            
        if row[0] == 'usage_stats':
            fname = extract_usage_stats(row[1], "static/data/{0}.csv".format(job_id))
            index = pairs.index(row)
            del pairs[index]
            if fname != "None":
                fname = "https://turingcompute.net/" + fname
            
    return template('./views/job_info',
                    title="Job - Info",
                    job_id=job_id,
                    usage_csv = fname,
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
    print "In browse : "
    session = bottle.request.environ.get('beaker.session')
    list_buckets = ["klab-webofscience", "klab-jobs"]

    r_bucket  =  request.params.get('bucket')
    r_key     =  request.params.get('key')

    print "Bucket :  ", r_bucket
    print "Key    :  ", r_key

    keys   = s3.list_s3_path(request.app, r_bucket, r_key)

    table = []
    headers = ["URL", "Size (B)", "Last Modified", "Storage Class"]
    # Find paths
    dirs       = []
    files      = []
    dirlookup  = []

    # Add parent link
    parent     = r_key.rsplit('/', 1)[0]
    if parent == r_key:
        parent = ""
    link = '<i><a href="{0}?bucket={1}&key={2}">{3}</a></i>'.format(request.app.get_url("/browse"),
                                                                    r_bucket,
                                                                    parent,
                                                                    "..")
    dirs.append([link, "Parent", "", ""])
    for key in keys:
        #Check if key is in current dir or a dir name
        relative_path = str((key.name).strip(r_key))
        print "Rel path : ", relative_path

        if relative_path.startswith('/'):
            relative_path = relative_path[1:]

        print "Rel path : ", relative_path

        print relative_path
        folder = relative_path.split('/')
        print "folder : ", folder
        if len(folder) > 1 : 
            dirname = ''
            if r_key :
                dirname = r_key + '/'

            link = '<i><a href="{0}?bucket={1}&key={2}">{3}</a></i>'.format(request.app.get_url("/browse"),
                                                                     r_bucket,
                                                                     dirname + folder[0],
                                                                     folder[0])
            item = [link, "Directory", key.last_modified, ""]
            if folder[0] not in dirlookup:
                dirlookup.append(folder[0])
                dirs.append(item)
            
        elif len(folder) == 1:
            path = '<a href="s3://{0}/{1}">{2}</a>'.format(r_bucket,
                                                           key.name,
                                                           key.name.split('/')[-1])
            files.append([path, utils.file_size_human(key.size), key.last_modified, key.storage_class])        

    table.append(headers)
    print table

    table.extend(dirs)
    print table
    table.extend(files)
    print table
    
    return template('./views/browser.tpl',
                    title = "/{0}/{1}".format(r_bucket, r_key),
                    table = table, # Body
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
    job_id   = str(uuid.uuid4())
    exp_time = tstamp_plus_nmins(60)
    bucket_name =  "klab-jobs" #"klab-webofscience" #
    print "Uploads page"

    vals = { "redirect_url" : "{0}/{1}".format(request.app.config["server.url"],
                                               "upload_confirm"),
             "aws_key_id"   : request.app.config["instance.tags"]["S3UploadKeyId"],
             "job_id"       : job_id,
             "exp_date"     : exp_time,
             "bucket_name"  : bucket_name
         }

    print "Uploading with key : {0}".format(request.app.config["instance.tags"]["S3UploadKeyId"])

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


@get('/tempkeys', method='GET', name="tempkeys")
def get_temp_keys():
    session  = bottle.request.environ.get('beaker.session')
    require_login(session)
    
    username = session["username"]
    try:
        user_info = identity.find_user_role(request.app, session["user_id"])
        # This is a vulnerability. We need to check everytime if the access_tokens 
        # are valid and alive with the api.amazon.com
        print user_info
        role      = "klab_public"
        creds     = sts.get_temp_creds(role)
        return template('./views/tempkeys.tpl',
                        username        = username,
                        session         = session,
                        AccessKeyId     = creds["AccessKeyId"],
                        SecretAccessKey = creds["SecretAccessKey"],
                        Token           = creds["SessionToken"],
                        Expiration      = creds["Expiration"],
                        title="Temporary keys",
                        alert=False)
        
    except Exception as e:
        return template('./views/logout.tpl',
                    username=username,
                    session=session,
                    title="Failed to get temporary keys",
                    alert=False)

##################################################################
# GET request should get a form to the user
# A button which would POST a request to upload a file directly
# to S3
##################################################################
@get('/login', method='GET', name="login")
def login():
    print request.headers.keys()
    if request.headers.get("X-Forwarded-Proto") != "https":
        print "Forwarding to https"
        redirect(request.app.config["server.url"] + "/login")

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
