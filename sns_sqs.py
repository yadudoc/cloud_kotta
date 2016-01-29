#!/usr/bin/env python

import boto
import sys
import json
import time
import boto.sqs
import config_manager as cm
import uuid

def get_uuid():
    return str(uuid.uuid1())

def publish(sns_conn, topicARN, message):
    sns_conn.publish(topic=topicARN, message=message)

def sns_test(sns_conn, topic_arn):
    uid = get_uuid()
    data = {"job_id"           : uid,
            "username"         : "yadu",
            "jobtype"          : "doc2vec",
            "inputs"           : [{"src": "https://s3.amazonaws.com/klab-jobs/inputs/test.txt", "dest": "test.txt" }],
            "outputs"          : [{"src": "doc_mat.pkl",  "dest": "klab-jobs/outputs/{0}/doc_mat.pkl".format(uid)},
                                  {"src": "word_mat.pkl", "dest": "klab-jobs/outputs/{0}/word_mat.pkl".format(uid)},
                                  {"src": "mdl.pkl",      "dest": "klab-jobs/outputs/{0}/mdl.pkl".format(uid)}],
            "submit_time"      : int(time.time()),
            "status"           : "pending"
    }
    print "Publishing Dummy task to SNS topic"
    publish(sns_conn, topic_arn, json.dumps(data))
    return data

def sqs_test(sqs_conn, queue_name):

    q   = sqs_conn.get_queue(queue_name)
    msg = q.get_messages(1)
    print len(msg)

    r = json.loads(msg[0].get_body())["Message"]
    print r
    print q.delete_message(msg[0])
    #req =  json.loads(msg[0].get_body()["Message"])

#sns_test(app.config["sns.conn"], app.config["instance.tags"]["JobsSNSTopicARN"])
#sqs_test(app.config["sqs.conn"], app.config["instance.tags"]["JobsQueueName"])
