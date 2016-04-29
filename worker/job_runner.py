#!/usr/bin/env python
# Ref: http://bottlepy.org/docs/dev/tutorial.html

import uuid
import time, datetime
import subprocess
import os
import glob
import json
import logging
import boto
import boto.ec2
import boto.sqs
from boto.s3.connection import S3Connection
import configurator
from bottle import route, run, get, post, request
from bottle import response
import base64, hmac, sha
import s3_funcs as s3
import sns_sqs
import ast

logging.basicConfig(filename='aws.log', level=logging.INFO)
configs = configurator.load_confs("configs")


################################################################
# Handle job execution
################################################################
def submit_job(src_bucket, key, dest_bucket):
    try :
        print "./run.sh {0} {1} {2}".format(src_bucket, key, dest_bucket)
        pid = subprocess.Popen(["./run.sh", src_bucket, key, dest_bucket])

    # Invalid value provided
    except ValueError:
        return 400
    # Failed to execute
    except OSError:
        return 500
    # Unknown error
    except :
        return 500

    # everything is OK!
    return 200

queue_name = 'yadunand-job-requests'
################################################################
# Job acquisition and job callout loop
################################################################
def annotate_loop(sqs):
    q = sqs.get_queue(queue_name)
    while 1:
        # Get only one message at a time. We only want to process
        # one at a time
        msg = q.get_messages(1)
        if msg:
            print msg
            sreq = json.loads(msg[0].get_body())["Message"]
            print sreq
            if not sreq :
                continue
            #data = json.loads(sreq)
            data  = ast.literal_eval(sreq)
            print "Received new request: {0}".format(data)
            src_bucket  =  data.get('s3_inputs_bucket')
            key         =  data.get('s3_key_input_file')
            dest_bucket =  'gas-results'
            status      =  submit_job(src_bucket, key, dest_bucket);
            q.delete_message(msg[0])
        print "Sleeping ."
        time.sleep(10)

    return

sns, sqs = sns_sqs.init()
annotate_loop(sqs)
