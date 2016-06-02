#!/usr/bin/env python
import boto
import sys
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import json
import time
import command
import os

def get_s3_conn(key_id, key_secret, token):
    s3   = S3Connection(aws_access_key_id=key_id,
                        aws_secret_access_key=key_secret,
                        security_token=token)
    return s3

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
        print "File size > 1MB. Using aws s3 cli"
        duration = fast_upload_s3_keys(s3conn, source, bucket_name, prefix, meta)
    else:
        print "File size < 1MB. Using upload_s3_keys"
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

# Download a key from the bucket
def fast_download_s3_keys(creds, bucket_name, prefix, target):
    env_vars = "AWS_ACCESS_KEY_ID={0};AWS_SECRET_ACCESS_KEY={1};AWS_SECURITY_TOKEN={2};AWS_DEFAULT_REGION={3}".format(creds["AccessKeyId"], creds["SecretAccessKey"], creds["SessionToken"], "us-east-1")
    cmd = "{3};aws s3 cp --region us-east-1 s3://{1}/{2} {0} ".format(target,
                                                                      bucket_name,
                                                                      prefix,
                                                                      env_vars)
    duration = command.execute_wait(None, cmd, None, None)
    return duration


# Download a key from the bucket
# Notes:
# Pending debug, using the temporary tokens we are not able to access the resources
# that are only accessible using a specific role.
def smart_download_s3_keys(s3conn, bucket_name, prefix, target, creds):
    start = time.time()
    try:
        bucket  = s3conn.get_bucket(bucket_name, validate=False)
        key     = bucket.get_key(prefix)
    except S3ResponseError :
        print "ERROR: Could not access the bucket"
        raise

    duration = key.get_contents_to_filename(target)
    return duration

    '''
    if key.size > 10*1024*1024 :
        print "File > 10Mb: downloading with s3 cli"
        duration = fast_download_s3_keys(creds, bucket_name, prefix, target)
    else:
        print "File < 10Mb: using get_contents_to_file"
        key.get_contents_to_filename(target)
        duration = time.time() - start

    return duration
    '''
    
def generate_signed_url(s3conn, bucket_name, prefix, duration):
    bucket  = s3conn.get_bucket(bucket_name, validate=False)
    try:
        key     = bucket.get_key(prefix)
        return key.generate_url(duration, method='GET')
    except:    
        return None

def test_uploads(app):
    upload_s3_keys(app.config["s3.conn"],
                   "web_server.log",
                   "klab-jobs",
                   "outputs/test/webserver.log",
                   {"Owner":"Yadu"})
    
    print fast_upload_s3_keys(app.config["s3.conn"],
                              "web_server.log",
                              "klab-jobs",
                              "outputs/test/webserver.log",
                              {"Owner":"Yadu"})

def list_s3_path(app, bucket_name, prefix):
    s3conn = app.config["s3.conn"]

    keys = None

    try:
        bucket = s3conn.get_bucket(bucket_name)
        keys = bucket.get_all_keys(prefix=prefix)

    except Exception, e:
        print "Caught exception with message {1}".format(e, e.error_message)

    return keys

def test_list(app):
    bucket_name = "klab-jobs"
    s3conn = app.config["s3.conn"]

    try:
        bucket = s3conn.get_bucket(bucket_name)
        keys = bucket.get_all_keys(prefix="inputs/")

    except Exception, e:
        print "Caught exception with message {1}".format(e, e.error_message)

    for key in keys:
        print key, key.size, key.last_modified

if __name__ == "__main__":
    import config_manager as cm
    app = cm.load_configs("production.conf")

    #test_uploads(app)
    test_list(app)
