#!/usr/bin/env python

import time, datetime
from datetime import datetime
import bottle
import logging
import argparse
import config_manager as conf_man
import os
import shutil
import sys
import boto.ec2.cloudwatch
import sns_sqs
import boto.dynamodb2 as ddb
import boto.dynamodb2.exceptions
import dynamo_utils as dutils
########################################################################################################
def kill_instance(app, instance_id, scale_group):
    """
    Kill a specific instance and decrement the desired capacity of the scaling group
    to which the instance belongs
    1. Detach the instance from the autoscaling group and decrement the desired number
       of instances by one. We should not kill instance before this step to ensure
       that the autoscaling group decides to terminate another instance by policy when
       we decrement the desired capacity.
    2. Once detached terminate the instance
    """
    autoscale = app.config["scale.conn"]
    current   = scale_group["current"]
    groupname = scale_group["groupname"]

    try:
        autoscale.detach_instances(groupname, [instance_id], decrement_capacity=True)
        logging.debug("Detaching instance {0} from autoscaling_group:{1}".format(instance_id, groupname))
        ec2 = app.config["ec2.conn"]    
        ec2.terminate_instances(instance_ids=[instance_id])
        logging.debug("Terminating instance {0}".format(instance_id))
    
    except Exception as e:        
        logging.error("Failed to remove instance{0} Caught exception : {0}".format(instance_id, e))
        return False

    return True
    
########################################################################################################
def get_autoscale_info(app, stack_name):
    """
    Given a cloudformation stack_name, get all autoscaling groups.
    Args:
         app object
         stack_name string name of the cloud formation stack
    returns:
         {} If no autoscaling group exits in the stack /or has a name starting with stack_name
         Returns a dict of dict with test and proc autoscaling groups
    """
    
    scale = app.config["scale.conn"]        
    myautoscale = [x for x in app.config["scale.conn"].get_all_groups() if x.name.startswith(stack_name)]
    
    autoscale = {}
    for grp in myautoscale:
        instances = grp.instances
        count     = len(instances)
        grp_name = grp.name[len(stack_name)+1:]
            
        if grp_name.startswith('Test'):
            autoscale['test'] = { "min"     : grp.min_size,
                                  "desired" : grp.desired_capacity,
                                  "max"     : grp.max_size,
                                  "current" : count,
                                  "instances" : instances,
                                  "groupname"     : grp.name}

        elif grp_name.startswith('Prod'):
            autoscale['prod'] = { "min"     : grp.min_size,
                                  "desired" : grp.desired_capacity,
                                  "max"     : grp.max_size,
                                  "current" : count,
                                  "instances" : instances,
                                  "groupname"     : grp.name }
            
        else:
            print "Error: could not find scaling groups"

    return autoscale

########################################################################################################
def post_message_to_pending(app, msg, active_q, pending_q):
    """
    Posts message to the pending queue
    """
    print msg
    #print json.loads(msg.get_body())["Message"]
    # Post message to pending_q
    sns_sqs.post_message_to_pending(app, pending_q, msg.get_body(), "job_id:none")
    # Delete message from the active_q
    active_q.delete_message(msg)
    return 

########################################################################################################
def check_job_status(app, msg, job_id, instance_id, autoscalegrp, active_q, pending_q):
    """
    Check the job status:
    Cover two situations :
        1. Job says it is active (by being in the active queue), but the instance is not running
        2. Job says it is active but underwent an accidental termination,
           Set up retry, with a counter.
    
    """
    ec2conn  = app.config["ec2.conn"]

    print "Instances in the current group : ", autoscalegrp["instances"]
    if instance_id in autoscalegrp["instances"]:
        # Check if the instance has gone rogue.
        # This is harder right now.
        print "[INFO] : job_id:{0} on instance_id{1} : {2}".format(job_id, instance_id, autoscalegrp["instances"])
    else:
        # Instance is missing. Job is clearly abandoned.
        # Job needs to go back in the queue.
        print "[INFO] : job_id:{0} on instance_id:{1} : BUT MISSING".format(job_id, instance_id)
        # Move job into the pending queue for rerun, but add info on this being a reattempt
        post_message_to_pending(app, msg, active_q, pending_q)
    return

########################################################################################################
def watch_loop(app):
    """
    Watch_loop looks at the definition of the autoscaling_groups and the active queues
    to determine whether :
        1. An instance needs to be removed from the scaling group and terminated
        2. A task has been in the active queue for long and appears to have timed out
           and needs to be moved to the pending queue, for re-attempt.
           Why would a task fail ?
           -> Hard error in task causes worker to fail
           -> Instance was lost mid run
              
    """
    status     = conf_man.update_creds_from_metadata_server(app)
    stack_name = app.config["instance.tags"]["aws:cloudformation:stack-name"]    
    autoscale  = get_autoscale_info(app, stack_name)
    print autoscale

    # Select all relevant queues in our cloudformation stack
    queues     = [q for q in app.config["sqs.conn"].get_all_queues() if q.name.startswith(stack_name)]
    # Select only the active queues
    active_q   = [q for q in queues if "Active" in q.name]
    pending_q  = [q for q in queues if "Active" not in q.name]

    for q in active_q:

        print "Active queue : ", q.name
        qtype = None
        
        if "Test" in q.name:
            qtype = "test"
        elif "Prod" in q.name:
            qtype = "prod"
        else:
            logging.error("Unknown queue : ".format(q.name))
            break

        # Find the corresponding pending queue to the current active queue
        p_q   = None
        p_qs = [pq for pq in pending_q if qtype in pq.name.lower()]
        if len(p_qs) == 1:
            p_q = p_qs[0]
            print "Pending queue : {0}".format(p_q)
        else:
            logging.error("Found too many pending queues : {0}".format(p_qs))
            exit(0)
                        
        print "Instances in this group : ", autoscale[qtype]["instances"]        
        for i in autoscale[qtype]["instances"]:
            print i.health_status
            print i.lifecycle_state


        while (1):
            """
            Here we get all messages in the current queue and check the following conditions:
            1. No more messages to check -> Break
            2. If messages exists
            -> Check if it is a kill_request.
            -> Kill the instance and decrement the autoscale group desired count
            -> 
            """
            messages = q.get_messages(num_messages=10, visibility_timeout=2, wait_time_seconds=1, message_attributes=['All'])                
            if not messages:
                break

            for msg in messages:
                # Check if message is a kill_request
                if msg.message_attributes["job_id"]["string_value"] == "kill_request":
                    logging.info("Received a kill_request from : ".format(msg.message_attributes["instance_id"]["string_value"]))
                    # Are there more machines than the minimum
                    if autoscale[qtype]["current"] > autoscale[qtype]["min"]:
                        logging.info("Instances in autoscale group current:{0} > min:{1}".format(autoscale[qtype]["current"], autoscale[qtype]["min"]))
                        logging.info("Kill : {0}".format(msg.message_attributes["instance_id"]["string_value"]))
                        kill_instance(app, msg.message_attributes["instance_id"]["string_value"], autoscale[qtype])                                    
                        q.delete_message(msg)
                        # Message is a regular job
                    else:
                        # We do not have excess machines. So no kill requests need to be made.
                        # However the message needs to be deleted
                        logging.info("Kill request ignored: {0}".format(msg.message_attributes["instance_id"]["string_value"]))
                        q.delete_message(msg)

                # If message is not a kill_request it is an active job.
                # Check if job has timed-out or the machine it is running on has
                # accidentally terminated 
                else:
                    job_id      = msg.message_attributes["job_id"]["string_value"]
                    instance_id = msg.message_attributes["instance_id"]["string_value"]

                    try:
                        record      = dutils.dynamodb_get(app.config["dyno.conn"], job_id)
                    except Exception, e:
                        print "JOb {0} not found in dynamodb"
                        print "Deleting the message"
                        q.delete_message(msg)                
                        record      = None
                        
                    if record and record["status"] in ["completed", "failed"]:
                        print "Job {0} is {1} -> Deleting the active job message".format(job_id, record["status"])
                        q.delete_message(msg)
                    else:
                        print "Job_id: {0}  Active on Instance: {1}".format(job_id, instance_id)
                        check_job_status(app, msg, job_id, instance_id, autoscale[qtype], q, p_q)
                    
    return None
        

########################################################################################################
if __name__ == "__main__":

   parser   = argparse.ArgumentParser()
   parser.add_argument("-v", "--verbose", default="DEBUG", help="set level of verbosity, DEBUG, INFO, WARN")
   parser.add_argument("-l", "--logfile", default="instance_watcher.log", help="Logfile path. Defaults to ./instance_watcher.log")
   parser.add_argument("-c", "--conffile", default="test.conf", help="Config file path. Defaults to ./test.conf")
   parser.add_argument("-j", "--jobid", type=str, action='append')
   parser.add_argument("-i", "--workload_id", default=None)
   args   = parser.parse_args()

   if args.verbose not in conf_man.log_levels :
      print "Unknown verbosity level : {0}".format(args.verbose)
      print "Cannot proceed. Exiting"
      exit(-1)

   logging.basicConfig(filename=args.logfile, level=conf_man.log_levels[args.verbose],
                       format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                       datefmt='%m-%d %H:%M')
   logging.getLogger('boto').setLevel(logging.CRITICAL)

   logging.debug("\n{0}\nStarting instance watcher\n{0}\n".format("*"*50))
   app = conf_man.load_configs(args.conffile);
   
   while 1:
       watch_loop(app)
       time.sleep(60)
       
   

   
   

