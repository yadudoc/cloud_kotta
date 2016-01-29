#!/usr/bin/env python
import boto
import sys
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import json


################################################################
# 1. Get s3connection object
# 2. Get the bucket from the connection
# 3. List the keys and inormation under the bucket for keys matching provided prefix
# Return a list of dicts
################################################################
def upload_s3_keys(s3conn, source, bucket_name, prefix, meta):
    bucket  = s3conn.get_bucket(bucket_name, validate=False)
    k       = Key(bucket)
    k.key   = prefix
    for m in meta:
        k.set_metadata(m, meta[m])

    k.set_contents_from_filename(source)
    k.set_metadata('time', "foo")

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
    key     = bucket.get_key(prefix)
    if key:
        return key.generate_url(duration, method='GET')
    else:
        return None

def test():
    import config_manager as cm
    app = cm.load_configs("production.conf")
    upload_s3_keys(app.config["s3.conn"],
                   "web_server.log",
                   "klab-jobs",
                   "outputs/test/webserver.log",
                   {"Owner":"Yadu"})

#test()
