#!/usr/bin/env python
from __future__ import print_function
import subprocess32 as subprocess
import os
import time
import shlex

############################################################################
# Default params
############################################################################
sleep_time = 5
USAGE_UPDATE_TIME = 120
WALLTIME_EXCEEDED = 1001
KILLED_BY_REQUEST = 1002


import os
import subprocess32 as subprocess

############################################################################
#Exit Reasons from http://www.tldp.org/LDP/abs/html/exitcodes.html

exit_reason = { 0   : None,
                1   : "General Error",
                2   : "Misuse of shell builtin",
                126 : "Command invoked cannot execute",
                127 : "Command not found",
                128 : "Invalid argument to exit",
                130 : "Script terminated by ctrl+C",
                128+9  : "Received sigkill: SIGKILL",
                128+13 : "Broken pipe : SIGPIPE",
                128+11 : "Invalid memory reference : SIGSEGV",
                128+15 : "Termination signal : SIGTERM"
}
############################################################################


def execute_wait (cmd, walltime, stdout_pipe=None, stderr_pipe=None) :
    start_t = time.time()
    
    std_out = stdout_pipe if stdout_pipe else open("staging.out.txt", 'a')
    std_err = stderr_pipe if stderr_pipe else open("staging.err.txt", 'a')
    
    ret     = {  'status'  : True,
                 'dur'     : None,
                 'exitcode': 0,
                 'reason'  : None
             }

    try :
        proc    = subprocess.Popen(cmd, stdout=std_out, stderr=std_err, shell=True, executable='/bin/bash')
        retcode = proc.wait()
        ret['exitcode'] = retcode
        ret['reason']   = exit_reason.get(retcode, "Unknown Reason")

    except OSError as e:
        print("Caught OS Error : {0}".format(e.errno))
        print("Caught OS Error : {0}".format(e.strerror))
        print("Caught OS Error : {0}".format(e))
        #print("Traceback       : {0}".format(e.child_traceback))
    except Exception as e:
        print("Caught exception : {0}".format(e))
        return -1

    total_t = time.time() - start_t
    ret['dur'] = total_t
    return ret


if __name__ == "__main__" :

    # Fail test
    cmd = "echo Helloworld"
    ret = execute_wait(cmd, None)
    print(ret)
    assert ret['exitcode'] == 0

    # Fail test
    cmd = "mango time"
    ret = execute_wait(cmd, None)
    print(ret)
    assert ret['exitcode'] == 127

    cmd = "git clone git:/asda"
    ret = execute_wait(cmd, None)
    print(ret)

    cmd = "echo hi; touch test"
    ret = execute_wait(cmd, None)
    print(ret)
    assert ret['exitcode'] == 0

    cmd = "git clone {0} {1}".format("https://github.com/yadudoc/TuringClient.git", "TuringClient")
    ret = execute_wait(cmd, None)
    print(ret)
    assert ret['exitcode'] == 0

    cmd = "rm -rf TuringClient"
    ret = execute_wait(cmd, None)
    print(ret)
    assert ret['exitcode'] == 0


    cmd = """git clone {0} {1};
    git --git-dir={1}/.git/ --work-tree={1}/ checkout {2}
    """.format("https://github.com/yadudoc/TuringClient.git",  # Source git
               "TuringClient", # Dest dir
               "b7bf44e6f5e69cdb86c60e54a7b2a304822f02a6" # Commit hash
    )
    ret = execute_wait(cmd, None)
    print(ret)
    assert ret['exitcode'] == 0
    
    
    cmd = "git --git-dir={0}/.git/ --work-tree={0}/ rev-parse HEAD ".format("TuringClient")
    ret = execute_wait(cmd, None, )
    print(ret)
    assert ret['exitcode'] == 0
    
    
    
