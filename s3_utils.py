#!/usr/bin/env python
import boto
import sys
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import json
import command
import os
################################################################
# 1. Get s3connection object
# 2. Get the bucket from the connection
# 3. List the keys and inormation under the bucket for keys matching provided prefix
# Return a list of dicts
################################################################
def upload_s3_keys(s3conn, source, bucket_name, prefix, meta):
    start = time.time()
    bucket  = s3conn.get_bucket(bucket_name, validate=False)
    k       = Key(bucket)
    k.key   = prefix
    for m in meta:
        k.set_metadata(m, meta[m])

    k.set_contents_from_filename(source)
    k.set_metadata('time', "foo")

    return time.time() - start

################################################################
# 1. Get s3connection object
# 2. Get the bucket from the connection
# 3. List the keys and inormation under the bucket for keys matching provided prefix
# Return a list of dicts
################################################################
def fast_upload_s3_keys(s3conn, source, bucket_name, prefix, meta):
    cmd = "aws s3 cp --region us-east-1 {0} s3://{1}/{2}".format(source,
                                                                 bucket_name,
                                                                 prefix)
    # execute_wait(app, cmd, walltime, job_id)
    duration = command.execute_wait(None, cmd, None, None)
    return duration


def smart_upload_s3_keys(s3conn, source, bucket_name, prefix, meta):
    
    # Use aws s3 cli only if file size is larger than 10 Mb
    if os.stat(source).st_size > 10*1024*1024:
        duration = fast_upload_s3_keys(s3conn, source, bucket_name, prefix, meta)
    else:
        duration = upload_s3_keys(s3conn, source, bucket_name, prefix, meta)

    return duration


# Download a key from the bucket
def download_s3_keys(s3conn, bucket_name, prefix, target):
    try:
        bucket  = s3conn.get_bucket(bucket_name, validate=False)
        key     = bucket.get_key(prefix)
    except S3ResponseError :
        print "ERROR: Could not access the bucket"
        raise

    print "filename", key
    key.get_contents_to_filename(target)
    return key


def generate_signed_url(s3conn, bucket_name, prefix, duration):
    bucket  = s3conn.get_bucket(bucket_name, validate=False)
    try:
        key     = bucket.get_key(prefix)
        return key.generate_url(duration, method='GET')
    except:    
        return None

def test():
    import config_manager as cm
    app = cm.load_configs("production.conf")
    '''
    upload_s3_keys(app.config["s3.conn"],
                   "web_server.log",
                   "klab-jobs",
                   "outputs/test/webserver.log",
                   {"Owner":"Yadu"})
    '''
    print fast_upload_s3_keys(app.config["s3.conn"],
                              "web_server.log",
                              "klab-jobs",
                              "outputs/test/webserver.log",
                              {"Owner":"Yadu"})


if __name__ == "__main__":
    test()
    
