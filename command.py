#!/usr/bin/env python

import subprocess
import threading
import os
import time

############################################################################
# Default params
############################################################################
sleep_time = 5
WALLTIME_EXCEEDED = 1001
KILLED_BY_REQUEST = 1002

############################################################################
# Run a command
############################################################################
def RunCommand (cmd, walltime, statecheck):
    
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

        if statecheck(cmd['job_id']) :
            print "Termination request received. killing process"
            proc.kill()
            return KILLED_BY_REQUEST

        time.sleep(sleep_time)

    print "RunCommand Completed {0}".format(cmd)



cmd = {"job_id"     : 123123,
       "executable" : "/bin/echo",
       "args"       : "hello"}
       
def foo():
    return False

status = RunCommand("/bin/doo Hello World", 5, foo)
if status == 127 :
    print "Pass"
else:
    print "Failed test"

status = RunCommand('/bin/echo "Hello World"; sleep 8', 10, foo)
if status == 0 :
    print "Pass"
else:
    print "Failed test"


