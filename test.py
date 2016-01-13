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

    print task_desc
    data = ast.literal_eval(task_desc)

    dutils.dynamodb_update(app.config["dyno.conn"], data)
    sns_sqs.publish(app.config["sns.conn"], app.config["instance.tags"]["JobsSNSTopicARN"],
                    json.dumps(task_desc))
    return uid


def cancel_task(app, jobid):
    print "Cancelling task : {0}".format(jobid)
    #record = dutils.dynamodb_get(app.config["dyno.conn"], jobid)

    record = dutils.dynamodb_get(app.config["dyno.conn"])
    print record
    
    
if __name__ == "__main__":

    parser   = argparse.ArgumentParser()
    parser.add_argument("-j", "--jobinfo",  help="json job description or jobid", required=True)
    parser.add_argument("-r", "--request",  help="Request type [submit, status, cancel]", required=True)
    parser.add_argument("-c", "--conffile", default="production.conf", help="Config file path. Defaults to ./test.conf")
    args   = parser.parse_args()

    if args.jobinfo :        
        print args.jobinfo

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




    

