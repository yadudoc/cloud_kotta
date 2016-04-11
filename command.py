#!/usr/bin/env python

import subprocess
import threading
import os
import time
import dynamo_utils as dutils
import config_manager as cm

############################################################################
# Default params
############################################################################
sleep_time = 5
USAGE_UPDATE_TIME = 120
WALLTIME_EXCEEDED = 1001
KILLED_BY_REQUEST = 1002

############################################################################
# Check dynamodb to ensure that the application has not been cancelled
############################################################################
def check_if_cancelled(app, job_id):
    if not job_id :
        return False

    print "Statecheck"
    cm.update_creds_from_metadata_server(app)
    record = dutils.dynamodb_get(app.config["dyno.conn"], job_id)
    if record["status"] == "cancelled":
        print "Cancelled"
        return True

    print "Job not cancelled"
    return False


def update_record(record, key, value):
   record[key] = value
   record.save(overwrite=True)
   return

############################################################################
# Update dynamodb with usage stats
############################################################################
def update_usage_stats(app, job_id):
    if not job_id :
        return False

    print "Updating usage_stats"

    try:
        cmd = ["/home/ubuntu/task_engine/system_stats.sh", "{0}".format(time.time())]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        out, err = proc.communicate()
    except Exception as e:
        print "Failed to run system_stats.sh"
        print "Caught exception : {0}".format(e)
        return
    
    cm.update_creds_from_metadata_server(app)
    record = dutils.dynamodb_get(app.config["dyno.conn"], job_id)

    old = record.get("usage_stats", "")
    current = old + out.strip('\n')
    st = update_record(record, "usage_stats", current)
    return

############################################################################
# Run a command
############################################################################
def execute (app, cmd, walltime, job_id, env_vars={}):
    
    start_t = time.time()
    print "RunCommand Started   {0}".format(cmd)

    std_out = open("STDOUT.txt", 'w')
    std_err = open("STDERR.txt", 'w')

    env = os.environ.copy()
    for k in env_vars:
        env[k] = env_vars[k]
    env["TURING_JOB_ID"] = job_id
    env["HOME"] = "/home/ubuntu"

    start_time = time.time()    
    proc = subprocess.Popen(cmd, stdout=std_out, stderr=std_err, env=env, shell=True)

    time.sleep(1)
    t_last_update = 0
    while True:

        delta   =  int(time.time() - start_time)        
        # Check if process has finished
        status  =  proc.poll()
        print status
        if status == None:
            print "Process is still active"
        else:
            print "Process exited with code {0}".format(status)
            return status

        if delta > walltime :
            print "Process exceeded walltime limits {0} > {1}".format(delta, walltime)
            proc.kill()
            return WALLTIME_EXCEEDED

        if check_if_cancelled(app, job_id) :
            print "Termination request received. killing process"
            proc.kill()
            return KILLED_BY_REQUEST

        # Update for the first time and subsequently everytime when
        # more than 60s has elapsed since t_last_update.
        if (t_last_update == 0) or ((delta - t_last_update) > USAGE_UPDATE_TIME) :
            update_usage_stats(app, job_id)
            t_last_update = delta

        time.sleep(sleep_time)
        
        
    total_t = time.time() - start_t    
    print "RunCommand Completed {0} in {1} s".format(cmd, total_t)
    return total_t

############################################################################
# Run a command
############################################################################
def execute_wait (app, cmd, walltime, job_id):
    start_t = time.time()
    std_out = open("exec_wait.out.txt", 'w')
    std_err = open("exec_wait.err.txt", 'w')
    start_time = time.time()    
    try :
        proc = subprocess.Popen(cmd, stdout=std_out, stderr=std_err, shell=True)
        proc.wait()
    except Exception as e:
        print "Caught exception : {0}".format(e)
        return -1

    total_t = time.time() - start_t

    print "RunCommand Completed {0}".format(cmd)
    return total_t

def testing():
    import config_manager as cm
    app = cm.load_configs("production.conf")
    cmd = {"job_id"     : 123123,
           "executable" : "/bin/echo",
           "args"       : "hello"}
       
    job_id = "ce19ede4-da29-48e5-abcf-2eff53778333"
    update_usage_stats(app, job_id)
    update_usage_stats(app, job_id)
    exit(0)
    
    status = execute(app, "/bin/doo Hello World", 5, None)
    if status == 127 :
        print "Pass"
    else:
        print "Failed test"

    status = execute(app, '/bin/echo "Hello World"; sleep 8', 10, None)
    if status == 0 :
        print "Pass"
    else:
        print "Failed test"
        
    cmd = {"job_id"     : 123123,
           "executable" : "aws",
           "args"       : "s3 cp {0} {1}".format("./dummy50m", "s3://klab-jobs/yadu/data/dummy50m") }

    print execute_wait(app, cmd, 50, "asdsada")

    cmd = {"job_id"     : 123123,
           "executable" : "aws",
           "args"       : "s3 cp {0} {1}".format("./dummy500m", "s3://klab-jobs/yadu/data/dummy500m") }

    print execute_wait(app, cmd, 50, "asdsada")

    cmd = {"job_id"     : 123123,
           "executable" : "aws",
           "args"       : "s3 cp {0} {1}".format("./dummy1g", "s3://klab-jobs/yadu/data/dummy1g") }

    print execute_wait(app, cmd, 50, "asdsada")

    cmd = {"job_id"     : 123123,
           "executable" : "aws",
           "args"       : "s3 cp {0} {1}".format("./shuf.txt", "s3://klab-jobs/yadu/data/dummy1g") }

    print execute_wait(app, cmd, 50, "asdsada")
    


if __name__ == "__main__" :
    testing()
