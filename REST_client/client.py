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
SUBMIT_URL=SERVER_URL+"/rest/v1/submit_task"
STATUS_URL=SERVER_URL+"/rest/v1/status_task"
CANCEL_URL=SERVER_URL+"/rest/v1/cancel_task"

def debug_print(string):
    if GLOBAL_VERBOSE :
        print string

def get_access_token(authfile):
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

    with open(task_desc_file, 'r') as f:
        task_desc = f.read()
    data                 = ast.literal_eval(task_desc)
    data["access_token"] = auth['access_token']
    #########################
    #print "-"*50
    #for k in data:
    #    print "{0}: {1}".format(k, data[k])
    #print "-"*50
    #########################

    r = requests.post(SUBMIT_URL, data=data)
    return r.json()

def cancel_task(jobid):
    debug_print("Cancelling task : {0}".format(jobid))
    debug_print ("{0} - {1} - {2}".format(record["job_id"], record["status"], record["reason"]))
    return True

def status_task(jobid):
    debug_print("Status task : {0}".format(jobid))
    status = {}
    record = requests.get(STATUS_URL + "/{0}".format(jobid))
    
    results = record.json()
    for item in results:
        print "{0:10}  | {1:50}".format(item, str(results[item]).strip())
        
    return results
    
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
            
        uid = submit_task(args.jobinfo, args.authfile)
        if uid["status"] == "Success":
            print "[{0}] Job_id: {1}".format(uid["status"], uid["job_id"])
        else:
            print "[{0}] Reason: {1}".format(uid["status"], uid["reason"])

    elif args.request.lower() == "status":
        results= status_task( args.jobinfo)
        print results["status"]

    elif args.request.lower() == "cancel":
        cancel_task( args.jobinfo)

    else:
        print "Unknown request"
        exit(-1)
    
    exit(0)




    

