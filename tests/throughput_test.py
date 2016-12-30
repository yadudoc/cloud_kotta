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

def submit_task_N(app, task_desc_file, count):
    qtype   = "Test"
    jobdur  = 0
    jobname = "tput_test_{0}_{1}_{2}s".format(count, qtype, jobdur)
    jobids  = []
    test_q  = app.config["sqs.conn"].get_queue("Turing2-0-TestSQS-16WUKXE5TAGER")
    attr = {"job_id": {"data_type"   : "String",
                       "string_value": "Test"}}
    sqs_conn = app.config["sqs.conn"]
    start   = time.time()
    messages = []
    for i in range(0,int(count)):
        uid = str(uuid.uuid1())

        job_desc= { "jobname"            : "{0}".format(jobname),
                    "job_id"             : uid,
                    "username"           : "Yadu",
                    "i_user_id"          : "amzn1.account.AEKWXVYINCBBNY5MPRMOYND6CWWA",
                    "i_user_role"        : "arn:aws:iam::{0}:role/{1}".format(968994658855, "klab_public"),
                    "user_email"         : "yadu@uchicago.edu",
                    "user_email"         : "yadunand@uchicago.edu",
                    "submit_time"        : int(time.time()),
                    "submit_stamp"       : str(time.strftime('%Y-%m-%d %H:%M:%S')),
                    "status"             : "pending",
                    "executable"         : "/bin/sleep {0}".format(jobdur),
                    "queue"              : "{0}".format(qtype),
                    "i_script_name"      : "test.sh",
                    "i_script"           : "#Nothing",
                    "jobtype"            : "script",
                    "outputs"            : "",
                    "walltime"           : "{0}".format(jobdur*2 + 1) }
        message = {
            "Type" : "Notification",
            "MessageId" : "1eed1b29-9094-5d3e-b368-54eb58645f37",
            "Message" : json.dumps(job_desc),
            "Signature" : "V6kijhKkNlnkPvybJ3njb83eeHRlTuoqqyrzWbsuMtuXSSsxctxyBjM/gM57RB3hSKsWCfLwtjwR9eg4Uy5D59knNjtHoHUpdMqjQPDR21lO1OZCU2gWLQR3C1wpvkwpGEgNl5jGFZF3yzpX6j0kG8NU1y5KLnRKz4LOh2FZyUXkoGxdomf/bWctWrrMy3YcJzv6NmXIyJmJ/xyWMbOnPu5uiz6SsY7uJ7/e371Kqm8NO0WWyPbiu3ZsqPSPn5Qd0LzQfZVbmAwya+eeXelewMDL6nqGKhyYZMdo6PSlDH4q7RxYAusg76mKNPmFT9KGpEZIG72z1+M44pvIdJxMcg==",
            "SigningCertURL" : "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-bb750dd426d95ee9390147a5624348ee.pem"
        }
                
        messages.extend([message])
        jobids.extend([uid])
        dutils.dynamodb_update(app.config["dyno.conn"], job_desc)

    print "Done writing jobs to DDB in {0}s".format(time.time() - start)
    start = time.time()
    for message in messages:
        sqs_conn.send_message(test_q, json.dumps(message))
        #sns_sqs.publish(app.config["sns.conn"], app.config["instance.tags"][qtype + "JobsSNSTopicARN"],
        #                job_desc)
    for j in jobids:
        print "[JOBIDS] : job_id:{0} ".format(j)
    print "Completed in {0}s".format(time.time() - start)
    return jobids

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
    parser.add_argument("-t", "--tput_count",  help="Number of tasks to submit", required=True)
    parser.add_argument("-c", "--conffile", default="production.conf", help="Config file path. Defaults to ./test.conf")
    parser.add_argument("-v", "--verbose",  dest='verbose', action='store_true', help="Verbose output")
    args   = parser.parse_args()

    if args.verbose is True:
        GLOBAL_VERBOSE=True

    app = conf_man.load_configs(args.conffile)

    if args.request.lower() == "submit":
        #uid = submit_task(app, args.jobinfo)
        uid = submit_task_N(app, args.jobinfo, args.tput_count)
        #print "Uid : {0}".format(uid)

    elif args.request.lower() == "status":
        status_task(app, args.jobinfo)

    elif args.request.lower() == "cancel":
        cancel_task(app, args.jobinfo)

    else:
        print "Unknown request"
        exit(-1)
    
    exit(0)




    

