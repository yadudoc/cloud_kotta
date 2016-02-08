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

############################################################################
# Run a command
############################################################################
def execute (app, cmd, walltime, job_id):
    
    start_t = time.time()
    print "RunCommand Started   {0}".format(cmd)

    std_out = open("STDOUT.txt", 'w')
    std_err = open("STDERR.txt", 'w')

    start_time = time.time()    
    proc = subprocess.Popen(cmd, stdout=std_out, stderr=std_err, shell=True)

    time.sleep(1)

    while True:

        delta   =  int(time.time() - start_time)
        # Check if process has finished
        status  = proc.poll()
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

        time.sleep(sleep_time)

    total_t = time.time() - start_t    
    print "RunCommand Completed {0} in {1} s".format(cmd, total_t)
    return total_t

############################################################################
# Run a command
############################################################################
def execute_wait (app, cmd, walltime, job_id):
    start_t = time.time()
    std_out = open("STDOUT.txt", 'w')
    std_err = open("STDERR.txt", 'w')
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
