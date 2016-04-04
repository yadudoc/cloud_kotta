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


# Send a message to the queue with message_attributes
def send_sqs_msg(conn, q, message, message_attr):
    print "Sending message"
    status = conn.send_message(q, message, message_attributes=message_attr)
    return status

# Get the right message from the queue
def get_msg_with_attr(conn, q,  message_attr):
    while (1):
        # Introduce a higher visibility timeout to avoid the refresher seeing the same 
        # items repeatedly.
        msg = q.read(visibility_timeout=10, wait_time_seconds=1, message_attributes=['All'])
        # Case 1 We have a valid message
        if msg:
            if "job_id" in msg.message_attributes and "type" in msg.message_attributes:
                # Case:2 Valid message, and the right message we are looking for
                if msg.message_attributes["job_id"]["string_value"] == message_attr["job_id"]["string_value"]:
                    if msg.message_attributes["type"]["string_value"] == message_attr["type"]["string_value"]:
                        print "We have a matching refresh job request"
                        print msg.get_body()
                        return msg
                # Case:3 Valid message but not the one we are looking for
                else:
                    # If we don't do anything here, the message itself will timeout and get picked up
                    # by the right worker.
                    continue                
        # Case:4 We have exhausted all the messages in the queue, and a message with the attributes we are
        # looking for are not found.
        else:
            print "[ERROR] Could not get the message for refresh cycle"
            return None
                    
    return None


def refresh_message(sqs_conn, q, msg):
    print "Refreshing message"
    print msg.get_body()
    m = json.loads(msg.get_body())
    job_id = m.get("job_id")

    attr = {"job_id": {"data_type"   : "String", 
                       "string_value": job_id},
            "type"  : {"data_type"   : "String", 
                       "string_value": "refresh"}}
    
    status  = send_sqs_msg(sqs_conn, q, msg.get_body(), attr)
    print "Send refresh message status : ", status
    new_msg = get_msg_with_attr(sqs_conn, q, attr)
    if msg:
        print "Found our message"
        print "deleting old message"
        q.delete_message(msg)
        
    else:
        print "No messages. Failed"

    sqs_conn.change_message_visibility(q, new_msg, 60*1)
    #sqs_conn.change_message_visibility(q, status, 60*1)
    return new_msg


def send_test_message(sqs_conn, q):
    job_id = get_uuid()
    attr = {"job_id": {"data_type"   : "String", 
                       "string_value": job_id},
            "type"  : {"data_type"   : "String", 
                       "string_value": "refresh"}}
    msg  = {"job_id"   : job_id,
            "walltime" : 400,
            "queue"    : "Test"}
    
    r = send_sqs_msg(sqs_conn, q, json.dumps(msg), attr)
    return r
    
if __name__ == "__main__":
    app = cm.load_configs("production.conf")

    sqs_conn = app.config["sqs.conn"]
    sqs_name = app.config["instance.tags"]["JobsQueueName"]
    
    q = sqs_conn.get_queue(sqs_name)

    r   = send_test_message(sqs_conn, q)
    msg = q.read(wait_time_seconds=10)
    print "Received a message"
    time.sleep(4)
    msg = refresh_message(sqs_conn, q, msg)
    
#sns_test(app.config["sns.conn"], app.config["instance.tags"]["JobsSNSTopicARN"])
#sqs_test(app.config["sqs.conn"], app.config["instance.tags"]["JobsQueueName"])
