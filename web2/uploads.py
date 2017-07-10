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


def generate_signed_url(app, filepath, user_id):
    print("In generate_url")
    expiry=3600
    url = app.config["s3.conn"].generate_url(3600, # expiry
                                             method='PUT', 
                                             bucket="klab-jobs",
                                             key="uploads/{0}/python/pkl/{1}".format(user_id,
                                                                                     filepath))

    return url

##################################################################################
# This is only a dummy function for get_url to generate a dynamic route
##################################################################################
@route('/rest/v1/upload_url', method='POST', name="post_upload_url")
def post_upload_url():

    session = bottle.request.environ.get('beaker.session')
    response.content_type = 'application/json'

    res, res_long = web_server.validate_tokens(request,session)

    if not res:
        print res_long
        return res_long        

    fpath = request.POST.get("filepath")

    try:
        url = generate_signed_url(request.app, fpath, user_id=session["user_id"])

    except Exception as e:
        return {"status" : "Fail",
                "reason" : "{0}".format(e)}

    return json.dumps({"status" : "Success", 
                       "upload_url" :  url})



if __name__ == "__main__":

    app = conf_man.load_configs("production.conf")
    url = generate_signed_url(app, "foo")
    print("Done: URL = {0}".format(url))
    
    os.system('curl --request PUT --upload-file ./upload_test "{0}"'.format(url))
