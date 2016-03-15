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
        row = [str(r["job_id"]), str(r["status"]),  
               str(r["jobtype"]), str(r["submit_stamp"])]
        table_tpl.append(row)

    table = sorted(table_tpl, key=lambda row: datetime.datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S'), reverse=True)
    return template("./views/jobs.tpl",
                    title="Task Status",
                    table=table,
                    session=session)

