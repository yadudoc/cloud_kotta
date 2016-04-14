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

def get_autoscale_info(app, stack_name):
    """
    Given a cloudformation stack_name, get all autoscaling groups.
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



def watch_loop(app):
    
    status     = conf_man.update_creds_from_metadata_server(app)
    stack_name = app.config["instance.tags"]["aws:cloudformation:stack-name"]    
    autoscale  = get_autoscale_info(app, stack_name)
    print autoscale

    for q in app.config["sqs.conn"].get_all_queues():
        if q.name.startswith(stack_name):
            # We only care about looking at the active queue here
            if "Active" not in q.name:                    
                continue
                    
            print "Active queue : ", q.name
            qtype = None
            if "Test" in q.name:
                qtype = "test"
            elif "Prod" in q.name:
                qtype = "prod"
            else:
                logging.error("Unknown queue : ".format(q.name))
                break

            print "Instances in this group : ", autoscale[qtype]["instances"]

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
                        # Are there more machines than the minimum
                        if autoscale[qtype]["current"] > autoscale[qtype]["min"]:
                            logging.info("Kill : {0}".format(msg.message_attributes["instance_id"]["string_value"]))
                            kill_instance(app, msg.message_attributes["instance_id"]["string_value"], autoscale[qtype])                                    
                            q.delete_message(msg)
                            # Message is a regular job
                        else:
                            job_id      = msg.message_attributes["job_id"]["string_value"]
                            instance_id = msg.message_attributes["instance_id"]["string_value"]
                            print "Job_id: {0}  Active on Instance: {1}".format(job_id, instance_id)
                                
    return None
        


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
       
   

   
   

