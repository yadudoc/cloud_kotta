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
import boto
import boto.ec2.cloudwatch
import boto.dynamodb2 as ddb
import boto.dynamodb2.exceptions

from boto.s3.lifecycle import Lifecycle, Transitions, Rule



def create_lifecycle_policy_glacier():
   transitions = Transitions()
   transitions.add_transition(days=30, storage_class='STANDARD_IA')
   transitions.add_transition(days=180, storage_class='GLACIER')
   # Omitting prefix option to match the whole bucket. prefix='*' is 
   rule = Rule(id='IA_30_Glacier_180', status='Enabled', transition=transitions) 
   lifecycle = Lifecycle()
   lifecycle.append(rule)      
   return lifecycle

def create_lifecycle_policy():
   transitions = Transitions()
   transitions.add_transition(days=30, storage_class='STANDARD_IA')
   # Omitting prefix option to match the whole bucket. prefix='*' is 
   rule = Rule(id='IA_30', status='Enabled', transition=transitions) 
   lifecycle = Lifecycle()
   lifecycle.append(rule)      
   return lifecycle
   

def test(bucketname):
   print "Trying : ", bucketname
   s3conn  = boto.connect_s3()
   bucket  = s3conn.get_bucket(bucketname)

   #create_lifecycle_policy(bucketname)   
   lcycle = create_lifecycle_policy()
   bucket.configure_lifecycle(lcycle)

   lifecycle = bucket.get_lifecycle_config()

   print lifecycle


def apply_policy_on_buckets(bucketlist):

   s3conn  = boto.connect_s3()

   lifecycle   = create_lifecycle_policy()
   bucketnames = []

   try:
      with open(bucketlist) as bfile:
         bucketnames = [l.strip() for l in bfile.readlines()]
   except Exception as e:
      logging.error("Caught exception in reading the bucketlist file : {0}".format(bucketlist))
      exit(-1)

   for bucketname in bucketnames:
      logging.debug("Creating policy for {0}".format(bucketname))
      
      try:         
         bucket  = s3conn.get_bucket(bucketname)
         bucket.configure_lifecycle(lifecycle)
         
      except Exception as e:
         logging.error("Caught {0} for {1}".format(e, bucketname))

   return 

   
   
########################################################################################################
if __name__ == "__main__":


   parser   = argparse.ArgumentParser()
   parser.add_argument("-v", "--verbose", default="DEBUG", help="set level of verbosity, DEBUG, INFO, WARN")
   parser.add_argument("-l", "--logfile", default="one_time.log", help="Logfile path. Defaults to ./one_time.log")
   parser.add_argument("-c", "--conffile", default="production.conf", help="Config file path. Defaults to ./production.conf")
   parser.add_argument("-b", "--buckets", required=True, default=None, help="File containing a list of buckets to apply lifecycle policies to")
   parser.add_argument("-j", "--jobid", type=str, action='append')
   args   = parser.parse_args()

   if args.verbose not in conf_man.log_levels :
      print "Unknown verbosity level : {0}".format(args.verbose)
      print "Cannot proceed. Exiting"
      exit(-1)

   logging.basicConfig(filename=args.logfile, level=conf_man.log_levels[args.verbose],
                       format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                       datefmt='%m-%d %H:%M')
   logging.getLogger('boto').setLevel(logging.CRITICAL)

   logging.debug("\n{0}\nStarting One time lifecycle configuration \n{0}\n".format("*"*50))
   app = conf_man.load_configs(args.conffile);
   
   #test("klab-test-lifecycle")
   apply_policy_on_buckets(args.buckets)
   print "Done"
