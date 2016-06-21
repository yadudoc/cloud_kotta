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
@route('/publish', method='GET', name="publish")
def url_maker_resubmit_job():    
    session = bottle.request.environ.get('beaker.session')
    return template("./views/error.tpl",
                    session=session,
                    error_str="You've requested an invalid Job Type")    


#################################################################
# Print a table form of jobs and statuses
#################################################################
@route('/published_jobs', method='GET', name="published_jobs")
def published_jobs():

    print "Hi"
    session = bottle.request.environ.get('beaker.session')
    require_login(session)
    current_user = session["user_id"]

    conf_man.update_creds_from_metadata_server(request.app)
    results = request.app.config["dyno.conn"].scan(i_ispublished__eq='1')
    table_tpl = []

    for r in results:
        print r
        jobinfourl = request.app.get_url('/jobs')+"/"+str(r["job_id"])
        joburl     = ''
        if r["jobname"] :
            joburl = '<a href="{0}">{1}</a>'.format(jobinfourl, r["jobname"])
        else:
            joburl = '<a href="{0}">{1}</a>'.format(jobinfourl, str(r["job_id"]))
                                                
        row = [joburl , str(r["description"]), str(r["username"]), str(r["publishdate"])]
        table_tpl.append(row)

    table = sorted(table_tpl, key=lambda row: datetime.datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S'), reverse=True)
    return template("./views/published_jobs.tpl",
                    title="Published Jobs",
                    table=table,
                    session=session)


##################################################################################
# Handles the different job types.
##################################################################################
@route('/publish/<jobid>', method='GET', name="publish_job")
def publish_job(jobid):
    session = bottle.request.environ.get('beaker.session')
    require_login(session)
    print session["username"]

    prefill = None
    print "In publish =============================="
    pairs = web_server.get_job_info(request, jobid);
    user  = filter(lambda x: x[0] == 'username', pairs)

    # Check if you own the job.
    # If you do not own the job you get an error message.
    if user[0][1] == session["username"]:
        print "Username matches"
    else:
        return template('./views/error.tpl',
                        error_str="You are not the owner of this job :{0} \nInsufficient permissions to publish job".format(jobid),
                        session=session)

    jobname  = filter(lambda x: x[0] == 'jobname', pairs)
    if jobname and jobname[0]:
        prefill = {'jobname' : jobname[0][1]}

    jobdesc  = filter(lambda x: x[0] == 'jobdesc', pairs)
    if jobdesc and jobdesc[0]:
        prefill['jobdesc'] = jobdesc[0][1]
    
    print "Prefill : ", prefill;
    #return {"foo"}
    return template('./views/publish_job.tpl',
                    title="Publish Job",
                    jobid=jobid,
                    prefill=prefill,
                    session=session)


##################################################################################
# Updates the job with publish info.
##################################################################################             
def update_job_for_publish(request, job_id):
    print "Updating job for publish"
    record = dutils.dynamodb_get(request.app.config["dyno.conn"], job_id)
    record["i_ispublished"]  = '1'
    record["jobname"]      = request.POST.get('jobname').strip()
    record["description"]  = request.POST.get('jobdesc').strip()
    record["publishdate"]  = str(time.strftime('%Y-%m-%d %H:%M:%S'))
    record.save(overwrite=True)
    return True
    
##################################################################################
# Called when user presses the publish button.
##################################################################################
@route('/publish_job', method='POST', name="publish_job_handle")
def publish_job_description():
    session = bottle.request.environ.get('beaker.session')
    conf_man.update_creds_from_metadata_server(request.app)
    
    job_id = request.POST.get('jobid')
    status = update_job_for_publish(request, job_id)
    
    print job_id, status

    return template("./views/publish_confirm.tpl",
                    job_id=job_id,
                    title="Publish Confirmation",
                    session=session)
        
