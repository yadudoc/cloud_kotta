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


def watch_loop(app):
    
    while 1:
        status = conf_man.update_creds_from_metadata_server(app)

        stack_name = app.config["instance.tags"]["aws:cloudformation:stack-name"]
        
        for q in app.config["sqs.conn"].get_all_queues():
            if q.name.startswith(stack_name):
                if "Active" in q.name:
                    
                    print "Stack queue : ", q.name
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
   

   
   

