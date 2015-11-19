#!/usr/bin/env python

import boto
import sys
import configurator
import json
import time
import boto.sqs

topic_arn  = 'arn:aws:sns:us-east-1:127134666975:yadunand-job-notifications'
queue_name = 'yadunand-job-requests'

def publish(sns, topic, message):
    sns.publish(topic=topic, message=message)


def sns_test():
    sns, sqs = init()
    data = {"job_id"           : "dummy-task",
            "username"         : "yadunand",
            "s3_inputs_bucket" : "gas-inputs",
            "s3_key_input_file": "yadunand/sdadas",
            "input_file_name"  : "foo.txt",
            "submit_time"      : int(time.time()),
            "status"           : "pending"
    }
    print "Publishing Dummy task to SNS topic"
    publish(sns, topic_arn, json.dumps(data))


def sqs_test():
    sns, sqs = init()
    #print sqs.get_all_queues()
    q   = sqs.get_queue(queue_name)
    msg = q.get_messages(1)
    print len(msg)
    req =  json.loads(msg[0].get_body()["Message"])
    print req

#sns_test()
#sqs_test()
