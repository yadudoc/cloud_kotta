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

#################################################################
# Print a table form of jobs and statuses
#################################################################
@route('/usage_stats', method='GET', name="usage_stats")
def usage_stats():

    session = bottle.request.environ.get('beaker.session')
    require_login(session)
    current_user = session["user_id"]

    conf_man.update_creds_from_metadata_server(request.app)
    results = request.app.config["dyno.conn"].scan(status__in=['active', 'staging_inputs', 'processing', 'staging_output'])
    table_tpl = []

    print "Jobs: "
    print "-"*50
    for r in results:
        print r["username"]
        row = [str(r["username"]), str(r["job_id"]), str(r["status"]),  
               str(r["jobtype"]), str(r["submit_stamp"]), str(r["queue"])]
        table_tpl.append(row)

    stackname = request.app.config["instance.tags"]["aws:cloudformation:stack-name"]
    myautoscale = [x for x in request.app.config["scale.conn"].get_all_groups() if x.name.startswith(stackname)]
    
    autoscale = {}
    for grp in myautoscale:
        instances = grp.instances
        count     = len(instances)
        print grp.name
        print grp.name.strip("{0}-".format(stackname))
        print grp.name.strip("{0}-".format(stackname)).startswith('Test')
        
        grp_name = grp.name[len(stackname)+1:]
        
        if grp_name.startswith('Test'):
            
            autoscale['test'] = [grp.min_size*100/grp.max_size,
                                 (count-grp.min_size)*100/grp.max_size,
                                 (grp.desired_capacity-count)*100/grp.max_size,
                                 grp.max_size]
            
        elif grp_name.startswith('Prod'):
            autoscale['prod'] = [grp.min_size*100/grp.max_size,
                                 (count-grp.min_size)*100/grp.max_size,
                                 (grp.desired_capacity-count)*100/grp.max_size,
                                 grp.max_size]
            
        else:
            print "Error: could not find scaling groups"


    print autoscale


    table = sorted(table_tpl, key=lambda row: datetime.datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S'), reverse=True)
    return template("./views/usage_stats.tpl",
                    title="Task Status",
                    table=table,
                    autoscale=autoscale,
                    session=session)

