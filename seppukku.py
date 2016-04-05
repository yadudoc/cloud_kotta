#!/usr/bin/env

import requests
import json
import time, datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta
import sns_sqs

metadata_server="http://169.254.169.254/latest/meta-data/"
clean_tmp_dirs = False

def get_instance_starttime() :
    try:
        data = requests.get(metadata_server + "local-ipv4")
        last_mod = data.headers['last-modified']
        return datetime.strptime(last_mod, "%a, %d %b %Y %H:%M:%S %Z")
    except e:
        print "Caught exception : {0}".format(e)

def kill_self(app, dry_run=False):
    instance_id = "foo"
    rc = app.config["ec2.conn"].terminate_instances(instance_ids=[instance_id], dry_run=dry_run)
    return rc

def request_kill_from_controller(app, dry_run=False):
    sqs_conn  = app.config["sqs.conn"]
    active    = app.config["instance.tags"]["ActiveQueueName"]
    active_q  = sqs_conn.get_queue(active)
        
    msg = {"job_id" : "kill_request",
           "dry_run" : str(dry_run)}

    job_id = "kill_request"
    sns_sqs.post_message_to_active(app, active_q, json.dumps(msg), job_id)
        

def die_at_hour_edge (app, dry_run=False) :
    # Die at 5 mins
    start_time   = get_instance_starttime()
    current_time = datetime.now()
    delta        =  current_time - start_time

    hours = delta.total_seconds() / (60*60)
    partial_hour =  ( delta.total_seconds() - int(hours)*60*60 ) /60

    print "Minutes from hour edge ", 60 - partial_hour

    if partial_hour > 58 :
        print "Time to die"
        #kill_self(app, dry_run=dry_run)
        request_kill_from_controller(app, dry_run=True)
    else:
        print "Wait till 2 mins to hour to die"
    
    return delta

if __name__ == "__main__" :
    import config_manager as cm
    app = cm.load_configs("production.conf")

    request_kill_from_controller(app, dry_run=False)

    
    while True:
        time.sleep(1)
        die_at_hour_edge(app)
