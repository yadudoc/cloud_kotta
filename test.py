#!/usr/bin/env python

import boto
import sys
import json
import time
import boto.sqs
import config_manager as conf_man
import uuid
import sns_sqs
import dynamo_utils as dutils
import argparse
import bottle
from bottle import template
import ast


def update_record(record, key, value):
    record[key] = value
    record.save(overwrite=True)
    return

def submit_task(app, task_desc_file):

    uid = str(uuid.uuid1())
    t   = int(time.time())
    tstamp = str(time.strftime('%Y-%m-%d %H:%M:%S'))

    task_desc = template(task_desc_file,
                         uid=uid,
                         time=t,
                         tstamp=tstamp)
    print "-"*50
    print task_desc
    print "-"*50
    data = ast.literal_eval(task_desc)

    dutils.dynamodb_update(app.config["dyno.conn"], data)
    sns_sqs.publish(app.config["sns.conn"], app.config["instance.tags"]["JobsSNSTopicARN"],
                    data)
    return uid

def debug_print(string):
    if GLOBAL_VERBOSE :
        print string

def cancel_task(app, jobid):
    debug_print("Cancelling task : {0}".format(jobid))

    record = dutils.dynamodb_get(app.config["dyno.conn"], jobid)
    tstamp = str(time.strftime('%Y-%m-%d %H:%M:%S'))

    update_record(record, "status", "cancelled")
    update_record(record, "reason", "User request cancel")
    update_record(record, "cancel_time", tstamp)
    debug_print ("{0} - {1} - {2}".format(record["job_id"], record["status"], record["reason"]))
    return True

def status_task(app, jobid):
    debug_print("Status task : {0}".format(jobid))

    record = dutils.dynamodb_get(app.config["dyno.conn"], jobid)
    status = {}

    if GLOBAL_VERBOSE:        
        for item in record.items():
            print "|{0:10}  | {1:50}".format(item[0], item[1])
        
    print record["status"]
    return record["status"]
    
GLOBAL_VERBOSE=False

if __name__ == "__main__":

    parser   = argparse.ArgumentParser()
    parser.add_argument("-j", "--jobinfo",  help="json job description or jobid", required=True)
    parser.add_argument("-r", "--request",  help="Request type [submit, status, cancel]", required=True)
    parser.add_argument("-c", "--conffile", default="production.conf", help="Config file path. Defaults to ./test.conf")
    parser.add_argument("-v", "--verbose",  dest='verbose', action='store_true', help="Verbose output")
    args   = parser.parse_args()

    if args.verbose is True:
        GLOBAL_VERBOSE=True

    app = conf_man.load_configs(args.conffile)

    if args.request.lower() == "submit":
        uid = submit_task(app, args.jobinfo)
        print "Uid : {0}".format(uid)

    elif args.request.lower() == "status":
        status_task(app, args.jobinfo)

    elif args.request.lower() == "cancel":
        cancel_task(app, args.jobinfo)

    else:
        print "Unknown request"
        exit(-1)
    
    exit(0)




    

