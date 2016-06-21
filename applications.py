#!/usr/bin/env python
import sys
import os
import subprocess
import logging
import command

UNKNOWN_ARGS = -5

def generic_executor(job_id, executable, args, inputs, outputs):
    try :
        print "Running {0} {1}".format(executable, args)
        std_out = open("STDOUT.txt", 'w')
        std_err = open("STDERR.txt", 'w')
        print [executable, args], "stdout='STDOUT.txt', stderr='STDERR.txt'"
        
        pid = subprocess.Popen([executable, args], stdout=std_out, stderr=std_err)
        pid.wait()
        std_out.close()
        std_err.close()
    # Invalid value provided
    except ValueError as e:
        logging.error("ValueError : {0}".format(e));
        raise

    # Failed to execute
    except OSError as e:
        logging.error("OSError : {0}".format(e));
        raise

    # Unknown error
    except Exception as e:
        logging.error("Generic Error : {0}".format(e));
        raise

    # everything is OK!
    return True

def script_executor (app, job_desc):

    inputs      = job_desc['inputs']
    walltime    = int(job_desc.get("walltime", 24*60*60))
    job_id      = job_desc["job_id"]
    script_file = job_desc.get('i_script_name')
    script      = job_desc.get('i_script').replace('\r\n', '\n')
    cmd         = job_desc["executable"]
    env         = {"wosuser"    : job_desc.get('i_wosuser', 'None'),                   
                   "wospasswd"  : job_desc.get('i_wospasswd', 'None')}

    with open(script_file, 'w') as ofile:
        ofile.write(script)
        os.chmod(script_file, 0o744)

    retcode  = 9999

    try:
        logging.debug("script_executor, executing {0}".format(cmd))
        retcode = command.execute(app, cmd, walltime, job_id, env)

    except Exception as e:
        logging.error("Caught exception : {0}".format(e))
        raise

    return retcode

def python_executor (app, job_desc):
    return True

def experimental (app, job_desc):
    return True


def doc_to_vec (app, job_desc):

    inputs   = job_desc['inputs']
    cmd      = "python /home/ubuntu/ncses/doc2vec/turing_updated_pipeline.py"
    walltime = int(job_desc.get("walltime", 24*60*60))
    job_id   = job_desc["job_id"]

    retcode  = 9999

    try:
        for i in inputs:
            if i["type"] == "doc":
                cmd = cmd + " -d {0}".format(i["dest"])

            elif i["type"] == "params":
                cmd = cmd + " -p {0}".format(i["dest"])

            elif i["type"] == "model":
                cmd = cmd + " -m {0}".format(i["dest"])

            else:
                return UNKNOWN_ARGS

        logging.debug("doc_to_vec, executing {0}".format(cmd))
        retcode = command.execute(app, cmd, walltime, job_id)

    except Exception as e:
        logging.error("Caught exception : {0}".format(e))
        raise

    return retcode

# Job Definitions
JOBS = { "doc_to_vec" : doc_to_vec,
         "generic"    : generic_executor,
         "script"     : script_executor,
         "python"     : python_executor,
         "experimental": experimental }


def test():
    uid="fasdsadsa"

    i = [{"src": "https://s3.amazonaws.com/klab-jobs/inputs/test.txt", "dest": "test.txt" }]
    o = [{"src": "doc_mat.pkl",  "dest": "klab-jobs/{0}/".format(uid)},
         {"src": "word_mat.pkl", "dest": "klab-jobs/{0}/".format(uid)},
         {"src": "mdl.pkl",      "dest": "klab-jobs/{0}/".format(uid)}]

    #JOBS["doc_to_vec"](i, o)
    r = JOBS["generic"]("job_1001", "/home/ubuntu/task_engine/test.sh", "foobar", [], [])
    print "Return code ", r

#test()
