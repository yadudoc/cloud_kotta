#!/usr/bin/env python

import boto
import sys
import json
import time
import boto.sqs
import config_manager as cm
import uuid
import sns_sqs
import dynamo_utils as dutils

def submit_task():
    app = cm.load_configs("production.conf")
    uid = str(uuid.uuid1())
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

    dutils.dynamodb_update(app.config["dyno.conn"], data)
    
    sns_sqs.publish(app.config["sns.conn"], app.config["instance.tags"]["JobsSNSTopicARN"],
                    json.dumps(data))


submit_task()
