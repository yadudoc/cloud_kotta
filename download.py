#!/usr/bin/env python

import re

def get_file(filename):
    if filename.startswith("http://"):
        print "Http get"

    if re.search("https://s3.*amazonaws.com/", filename):
        s3_path = re.sub("https://s3.*amazonaws.com/", "", filename)
        tmp     = s3_path.split('/', 1)
        s3_bucket = tmp[0]
        s3_key    = tmp[1]
        destination = s3_path.rsplit('/',1)[-1]
        print s3_bucket
        print s3_key
        print destination
    else:
        print "No match. Could not fetch data"

m_data="https://s3.amazonaws.com/klab-jobs/inputs/misha/plos_one/refs_0.pickle" 
get_file(m_data)


