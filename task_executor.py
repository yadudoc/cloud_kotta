#!/usr/bin/env python
import requests
import time, datetime
from datetime import datetime
import bottle
import logging
import argparse
import ast
from bottle import run, route, get, post, request, response
import json
import config_manager as conf_man
import task_executor_utils as utils
import os
import applications as apps
import s3_utils as s3
import dynamo_utils as dutils
import re
import shutil

metadata_server="http://169.254.169.254/latest/meta-data/"

def get_instance_starttime() :
   try:
      data = requests.get(metadata_server + "local-ipv4")
      last_mod = data.headers['last-modified']
      return datetime.strptime(last_mod, "%a, %d %b %Y %H:%M:%S %Z")
   except e:
      print "Caught exception : {0}".format(e)

def get_metainfo() :
   try:
      data = requests.get(metadata_server + "")
      last_mod = data.headers['last-modified']
      return datetime.strptime(last_mod, "%a, %d %b %Y %H:%M:%S %Z")
   except e:
      print "Caught exception : {0}".format(e)


##################################################################
# A rudimentary times for coarse-grained profiling
##################################################################
class Timer(object):
   def __init__(self, verbose=False):
      self.verbose = verbose

      def __enter__(self):
         self.start = time.time()
         return self

      def __exit__(self, *args):
         self.end = time.time()
         self.secs = self.end - self.start
         self.msecs = self.secs * 1000  # millisecs
         if self.verbose:
            print 'elapsed time: %f ms' % self.msecs

def get_inputs(app, inputs, auth):
   print "In get_inputs"
   if not inputs:
      return

   for i in inputs:
      print "Staging_inputs : ", i

      if i["src"].startswith("http://"):
         print "Downloading {0} via http".format(i["src"])
         utils.download_file(i["src"], i["dest"])
      
      elif re.search("https://s3.*amazonaws.com/", i["src"]):
         s3_path = re.sub("https://s3.*amazonaws.com/", "", i["src"])
         tmp     = s3_path.split('/', 1)
         s3_bucket = tmp[0]
         s3_key    = tmp[1]
         #destination = s3_path.rsplit('/',1)[-1]
         print s3_bucket
         print s3_key
         print "Downloading {0} via s3 provider".format(i["src"])
         try:
            s3.download_s3_keys(app.config["s3.conn"],
                                s3_bucket,
                                s3_key,
                                i["dest"])
         except Exception, e:
            print "Download from s3 failed "
            raise

      elif i["src"].startswith("s3://"):

         
         tmp     = s3_path.split('/', 1)
         s3_bucket = tmp[0]
         s3_key    = tmp[1]
         #destination = s3_path.rsplit('/',1)[-1]
         print s3_bucket
         print s3_key
         print "Downloading {0} via s3 provider".format(i["src"])
         try:
            s3.download_s3_keys(app.config["s3.conn"],
                                s3_bucket,
                                s3_key,
                                i["dest"])
         except Exception, e:
            print "Download from s3 failed "
            raise

      else:
         print "No match. Could not fetch data"
      
   return


def put_outputs(app, outputs):
   print "In put_outputs"
   if not outputs:
      return

   for out in outputs:
      print "Outputs : ", out
      if not os.path.exists(out["src"]):
         print "Missing file. Continuing"
         continue

      target = out["dest"].split('/', 1)

      s3.upload_s3_keys(app.config["s3.conn"],
                        out["src"], # Source filename
                        target[0],  # Bucket name
                        target[1],  # Prefix
                        {"Owner": "Yadu"})

   return

def update_record(record, key, value):
   record[key] = value
   record.save(overwrite=True)
   return

   
def exec_job(app, jobtype, job_id, executable, args, inputs, outputs, data, auth):

   # Save current folder and chdir to a temporary folder
   conf_man.update_creds_from_metadata_server(app)

   cwd    = os.getcwd()
   tmpdir = "/tmp/task_executor_jobs/{0}".format(job_id)
   try:
      os.makedirs(tmpdir)
   except:
      print "Tmpdir {0} exists. Deleting and recreating".format(tmpdir)
      shutil.rmtree(tmpdir)
      os.makedirs(tmpdir)

   os.chdir(tmpdir)

   record = dutils.dynamodb_get(app.config["dyno.conn"], job_id)

   # Download data to the temp folder
   update_record(record, "status", "staging_inputs")
   try:
      get_inputs(app, inputs, auth)
   except Exception, e:
      update_record(record, "ERROR", "Failed to download inputs {0}".format(e))
      update_record(record, "status", "failed")
      update_record(record, "complete_time", time.time())
      logging.error("Failed to download inputs")
      return False


   # Execute the task
   update_record(record, "status", "processing")
   if jobtype not in apps.JOBS:
      logging.error("Jobtype : {0} does not exist".format(jobtype))
      print "Unable to process jobtype : {0}".format(jobtype)
      return False
   print "JOBS : ", apps.JOBS[jobtype]

   status = True
   returncode = 0
   try:
      returncode = apps.JOBS[jobtype](app, data)
      conf_man.update_creds_from_metadata_server(app)

   except Exception, e:
      update_record(record, "status", "Failed");
      update_record(record, "complete_time", time.time())
      update_record(record, "ERROR", str(e));
      print "Job execution failed : {0}".format(e)
      status = False

   update_record(record, "status", "staging_outputs")
   # Upload the result to S3
   put_outputs(app, outputs)

   if returncode != 0 :
      update_record(record, "status", "failed");
      update_record(record, "complete_time", time.time())
      update_record(record, "ERROR", str(e));
      update_record(record, "ERROR_CODE", returncode);
      status = False
   else:
      update_record(record, "status", "completed")
      update_record(record, "complete_time", time.time())

   # Chdir back to the original folder
   os.chdir(cwd)
   return True

def task_loop(app):
   sqs_conn = app.config["sqs.conn"]
   sqs_name = app.config["instance.tags"]["JobsQueueName"]

   q = sqs_conn.get_queue(sqs_name)

   while 1:
      msg = q.read(wait_time_seconds=20)
      if msg:
         # Too many things could fail here, do a blanket
         # Try catch
         try:
            sreq = json.loads(msg.get_body())["Message"]

            if not sreq :
               continue

            
            data        =  ast.literal_eval(sreq)
            print "Data : {0}".format(data)
            job_id      =  data.get('job_id')
            jobtype     =  data.get('jobtype')
            executable  =  data.get('executable')
            args        =  data.get('args')
            inputs      =  data.get('inputs')
            inputs      =  data.get('inputs')
            outputs     =  data.get('outputs')
            user_auth   =  {"user"      : data.get('i_user'),
                            "role"      : data.get('i_role'),
                            "token"     : data.get('i_token'),
                            "keyid"     : data.get('i_keyid'),
                            "keysecret" : data.get('i_keysecret')}
            
            print "Data : {0}".format(data)

            for key in data:
               print "{0} : {1}".format(key, data[key])

            status      =  exec_job(app,
                                    jobtype,
                                    job_id,
                                    executable,
                                    args,
                                    inputs,
                                    outputs,
                                    data,
                                    user_auth)
            

            print "Status : ", status

            if status == True:
               conf_man.send_success_mail(data, app)
            else:
               conf_man.send_failure_mail(data, app)

            # TODO : CLeanup
            print "At deletion : ", msg
            res = q.delete_message(msg)
            print "Deleting message from queue, status : ",res;

         except Exception, e:
               # The stdout/stder are being logged into a file
               # on the machine
               print "Job failed to complete : {0}".format(e)
               #pass

      else:
         print "{0}: Waiting for job description".format(time.time())
         logging.debug("{0}: Waiting for job description".format(time.time()))

      conf_man.update_creds_from_metadata_server(app)


if __name__ == "__main__":

   parser   = argparse.ArgumentParser()
   parser.add_argument("-v", "--verbose", default="DEBUG", help="set level of verbosity, DEBUG, INFO, WARN")
   parser.add_argument("-l", "--logfile", default="web_server.log", help="Logfile path. Defaults to ./web_server.log")
   parser.add_argument("-c", "--conffile", default="test.conf", help="Config file path. Defaults to ./test.conf")
   parser.add_argument("-j", "--jobid", type=str, action='append')
   parser.add_argument("-i", "--workload_id", default=None)
   args   = parser.parse_args()

   if args.verbose not in conf_man.log_levels :
      print "Unknown verbosity level : {0}".format(args.verbose)
      print "Cannot proceed. Exiting"
      exit(-1)

   print get_instance_starttime()
   exit(0)
   logging.basicConfig(filename=args.logfile, level=conf_man.log_levels[args.verbose],
                       format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                       datefmt='%m-%d %H:%M')

   logging.debug("\n{0}\nStarting task_executor\n{0}\n".format("*"*50))
   app = conf_man.load_configs(args.conffile);

   task_loop(app)

