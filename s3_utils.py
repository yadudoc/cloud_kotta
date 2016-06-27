#!/usr/bin/env python
import boto
import sys
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import json
import time
import command
import os
#from boto.exception import S3ResponseError

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
    except Exception, e :
        print "ERROR: Failed to download data : ", e
        raise

    print "filename", key
    key.get_contents_to_filename(target)
    return key

# Download a key from the bucket
def fast_download_s3_keys(creds, bucket_name, prefix, target):
    env_vars = "export AWS_ACCESS_KEY_ID={0};export AWS_SECRET_ACCESS_KEY={1};export AWS_SECURITY_TOKEN={2};export AWS_DEFAULT_REGION={3}".format(creds["AccessKeyId"], creds["SecretAccessKey"], creds["SessionToken"], "us-east-1")
    cmd = "{3};aws s3 cp --region us-east-1 s3://{1}/{2} {0} ".format(target,
                                                                      bucket_name,
                                                                      prefix,
                                                                      env_vars)
    duration = command.execute_wait(None, cmd, None, None)
    return duration


# Download a key from the bucket
def smart_download_s3_keys(s3conn, bucket_name, prefix, target, creds):
    start = time.time()

    try:
        bucket   = s3conn.get_bucket(bucket_name, validate=False)
        key      = bucket.get_key(prefix)

        if key.size > 10*1024*1024 :
            print "File > 10Mb: downloading with s3 cli"
            duration = fast_download_s3_keys(creds, bucket_name, prefix, target)
        else:
            print "File < 10Mb: using get_contents_to_file"
            key.get_contents_to_filename(target)
            duration = time.time() - start

    except boto.exception.S3ResponseError, e :
        print "ERROR: Caught S3ResponseError: ", e
        return -1 

    except Exception, e:
        print "ERROR: Could not access the bucket"
        raise

    return duration

    
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
    import sts
    import s3_utils as s3
    rolestring  = '' # Left out due to security concerns
    if not rolestring :
        print "Fill out rolestring to continue tests"

    creds = sts.get_temp_creds(rolestring)
    s3conn  = get_s3_conn( creds["AccessKeyId"],
                           creds["SecretAccessKey"],
                           creds["SessionToken"] )
    
    
    bucket_name = "klab-webofscience"
    prefix = 'raw_zipfiles/1976_DSSHPSH.zip'
    target = '/tmp/1976_DSSHPSH.zip'
    
    print "Listing items:"
    bucket = s3conn.get_bucket(bucket_name)
    print "getting keys:"
    keys   = bucket.get_all_keys(prefix="raw_zipfiles")
    for key in keys:
        print key , key.size, key.last_modified
    exit(0)
    #test_uploads(app)
    #test_list(app)
    #smart_download_s3_keys(s3conn, 
    #                       bucket_name, 
    #                       prefix, 
    #                       target, creds)

    #print fast_download_s3_keys(creds, bucket_name, prefix, target)
    print download_s3_keys(s3conn, bucket_name, prefix, target)
