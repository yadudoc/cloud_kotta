#!/usr/bin/env python

import config_manager as cm
import dynamo_utils as du
import sys


if __name__ == "__main__" :

    jobname = sys.argv[1]
    if not jobname :
        print "Needs a jobname as arg"
        exit(0)
    
    app = cm.load_configs("production.conf")
    results = app.config["dyno.conn"].scan(jobname__eq=jobname)
    for r in results:
        print "Deleting {0}-{1}".format(r['jobname'], r['job_id'])
        r.delete()
        
