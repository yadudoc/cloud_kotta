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

def get_connection(app):
    cloudwatch  = boto.ec2.cloudwatch.connect_to_region(app.config["identity"]['region'],
                                                    aws_access_key_id=app.config['keys.key_id'],
                                                    aws_secret_access_key=app.config['keys.key_secret'],
                                                    security_token=app.config['keys.key_token'])
    return cloudwatch

def watch_loop(app):
    
    cloudwatch = get_connection(app)
    while 1:
        status = conf_man.update_creds_from_metadata_server(app)
        if status :
            cloudwatch = get_connection(app)

        for q in app.config["sqs.conn"].get_all_queues():
            q_attr   = q.get_attributes()
            visible  = q_attr['ApproximateNumberOfMessages']
            inflight = q_attr['ApproximateNumberOfMessagesNotVisible']        
            total    = visible+inflight            
            r= cloudwatch.put_metric_data("SQS", 
                                          "ApproximateNumberOfTotalMessages", 
                                          value=total, 
                                          unit="Count",
                                          dimensions = {"QueueName" : q.name})
            logging.debug("[{0}] queue:{1} Total:{2} Visible:{3} Inflight:{4}".format(datetime.now().isoformat(),
                                                                                      q.name,
                                                                                      total,
                                                                                      visible,
                                                                                      inflight))
            print r
        time.sleep(60)

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




