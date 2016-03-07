#!/usr/bin/env python

import boto
import sys
import json
import time
import boto.sqs
import uuid
import argparse
import bottle
from bottle import template
import ast
from urlparse import urlparse
import requests


SERVER_URL="http://52.2.217.165:8888"

def get_access_token(authfile):
    print "Authfile : ", authfile
    url  = open(authfile, 'r').read()
    url_parts = urlparse(url)
    parts = url_parts.query.split('&')
    auth  = {}
    for p in parts:
        args = p.split('=')
        auth[args[0]] = args[1]        
    return auth

def submit_task(task_desc_file, auth_file):

    uid = str(uuid.uuid1())
    auth = get_access_token(auth_file)

    t   = int(time.time())
    tstamp = str(time.strftime('%Y-%m-%d %H:%M:%S'))

    with open(task_desc_file, 'r') as f:
        task_desc = f.read()
    data = ast.literal_eval(task_desc)
    data["job_id"] = uid

    #########################
    print "-"*50
    for k in data:
        print "{0}: {1}".format(k, data[k])
    print "-"*50
    #########################

    r = requests.post(SERVER_URL + "/rest/submit_task", data={"job_desc"     : json.dumps(data),
                                                              "access_token" : auth['access_token'] })
    #print r.json()
    return r

def debug_print(string):
    if GLOBAL_VERBOSE :
        print string

def cancel_task(jobid):
    debug_print("Cancelling task : {0}".format(jobid))

    #record = dutils.dynamodb_get(app.config["dyno.conn"], jobid)
    tstamp = str(time.strftime('%Y-%m-%d %H:%M:%S'))

    update_record(record, "status", "cancelled")
    update_record(record, "reason", "User request cancel")
    update_record(record, "cancel_time", tstamp)
    debug_print ("{0} - {1} - {2}".format(record["job_id"], record["status"], record["reason"]))
    return True

def status_task(jobid):
    debug_print("Status task : {0}".format(jobid))

    status = {}

    r = requests.post(SERVER_URL + "/rest/status_task", data={"job_desc"     : json.dumps(data),
                                                              "access_token" : auth['access_token'] })
    
    if GLOBAL_VERBOSE:        
        for item in record.items():
            print "|{0:10}  | {1:50}".format(item[0], item[1])
        
    print record["status"]
    return record["status"]
    
GLOBAL_VERBOSE=False

        
    
if __name__ == "__main__":

    parser   = argparse.ArgumentParser()
    parser.add_argument("-j", "--jobinfo",  help="json job description or jobid", required=True)
    parser.add_argument("-a", "--authfile", help="File with auth info")
    parser.add_argument("-r", "--request",  help="Request type [submit, status, cancel]", required=True)
    parser.add_argument("-c", "--conffile", default="production.conf", help="Config file path. Defaults to ./test.conf")
    parser.add_argument("-v", "--verbose",  dest='verbose', action='store_true', help="Verbose output")
    args   = parser.parse_args()


    if args.verbose is True:
        GLOBAL_VERBOSE=True

    #app = conf_man.load_configs(args.conffile)

    if args.request.lower() == "submit":
        if not args.authfile :
            print "[ERROR] Authfile missing. Cannot submit job without authfile"
            exit(-1)
            
        print get_access_token(args.authfile)
        uid = submit_task(args.jobinfo, args.authfile)
        print "Uid : {0}".format(uid)

    elif args.request.lower() == "status":
        status_task( args.jobinfo)

    elif args.request.lower() == "cancel":
        cancel_task( args.jobinfo)

    else:
        print "Unknown request"
        exit(-1)
    
    exit(0)




    

