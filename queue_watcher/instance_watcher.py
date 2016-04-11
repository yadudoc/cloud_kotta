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

    ec2 = app.config["ec2.conn"]
    print "Sent terminate request"
    ec2.terminate_instances(instance_ids=[instance_id])
    
    autoscale = app.config["scale.conn"]
    current = scale_group["current"]
    groupname = scale_group["groupname"]
    
    autoscale.set_desired_capacity(groupname, current-1)
    print "Scaled desired capacity to : {0}".format(current-1)
    return 

def get_autoscale_info(app, stack_name):
    scale = app.config["scale.conn"]        
    myautoscale = [x for x in app.config["scale.conn"].get_all_groups() if x.name.startswith(stack_name)]
    
    autoscale = {}
    for grp in myautoscale:
        instances = grp.instances
        count     = len(instances)
        print grp.name
        print grp.name.strip("{0}-".format(stack_name))
        print grp.name.strip("{0}-".format(stack_name)).startswith('Test')
        
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
    
    while 1:
        status = conf_man.update_creds_from_metadata_server(app)

        stack_name = app.config["instance.tags"]["aws:cloudformation:stack-name"]    

        autoscale  = get_autoscale_info(app, stack_name)
        print autoscale

        for q in app.config["sqs.conn"].get_all_queues():
            if q.name.startswith(stack_name):
                if "Active" in q.name:                    
                    print "Active queue : ", q.name
                    
                    qtype = None
                    if "Test" in q.name:
                        qtype = "test"
                    elif "Prod" in q.name:
                        qtype = "prod"
                    else:
                        print "Unknown queue : ", q.name
                        break

                    print "Instances in this group : ", autoscale[qtype]["instances"]

                    while (1):
                        messages = q.get_messages(num_messages=10, visibility_timeout=2, wait_time_seconds=1, message_attributes=['All'])
                        if not messages:
                            break
                        for msg in messages:
                            # Check if message is a kill_request
                            if msg.message_attributes["job_id"]["string_value"] == "kill_request":
                                # Are there more machines than the minimum
                                if autoscale[qtype]["current"] > autoscale[qtype]["min"]:
                                    print "Kill : {0}".format(msg.message_attributes["instance_id"]["string_value"])
                                    kill_instance(app, msg.message_attributes["instance_id"]["string_value"], autoscale[qtype])
                                    
                                q.delete_message(msg)
                            # Message is a regular job
                            else:
                                job_id      = msg.message_attributes["job_id"]["string_value"]
                                instance_id = msg.message_attributes["instance_id"]["string_value"]
                                print "Job_id: {0}  Active on Instance: {1}".format(job_id, instance_id)
    
        time.sleep(60)
    return None
        


if __name__ == "__main__":

   parser   = argparse.ArgumentParser()
   parser.add_argument("-v", "--verbose", default="DEBUG", help="set level of verbosity, DEBUG, INFO, WARN")
   parser.add_argument("-l", "--logfile", default="queue_watcher.log", help="Logfile path. Defaults to ./task_executor.log")
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

   logging.debug("\n{0}\nStarting task_executor\n{0}\n".format("*"*50))
   app = conf_man.load_configs(args.conffile);
   watch_loop(app)
   

   
   

