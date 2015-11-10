#!/usr/bin/env python
import requests
import datetime
from datetime import datetime
import bottle
import logging
import argparse
from bottle import run, route, get, post, request, response
import json
import config_manager as conf_man

metadata_server="http://169.254.169.254/latest/meta-data/"

def get_instance_starttime() :
   try:
      data = requests.get(metadata_server + "local-ipv4")
      last_mod = data.headers['last-modified']
      return datetime.strptime(last_mod, "%a, %d %b %Y %H:%M:%S %Z")
   except e:
      print "Caught exception : {0}".format(e)
   print "foo"


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

    logging.basicConfig(filename=args.logfile, level=conf_man.log_levels[args.verbose],
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M')

    logging.debug("\n{0}\nStarting webserver\n{0}\n".format("*"*50))
    app = conf_man.load_configs(args.conffile);

