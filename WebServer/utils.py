#!/usr/bin/env python
import math
import bottle
from bottle import template
from bottle import route, get, post, request, hook, redirect
import base64, hmac, sha
import logging

#################################################################################
# Some global vars
#################################################################################
JobTypes = ["doc_to_vec", "script"]

########################################################################################################
def require_login(session):
    """
    Helper function to ensure that the user is logged in
    Args:
        Takes the session dict
    Returns:
        If user is not logged in -> redirects the user to the login page
        else -> Does nothing
    """
    if not session:
        redirect("/login")
    if session.get("logged_in") != True:
        redirect("/login")

########################################################################################################
def file_size_human(size):
    """
    Convert file size to human friendly
    Args:
        size in bytes
    Returns:
        A string that has rescaled the size to appropriate exponent (Kilo/Mega/Giga...)
    """
    if size == 0 :
        return "0 B"
    suffix = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']
    index  = int(math.log(size, 1024))
    val    = size / math.pow(1024,index)
    return "{0:.2f} {1}".format(val, suffix[index])

########################################################################################################
def get_signature_and_policy(app, vals):
    """
    This function handles the creation of the encoded signature and policy.
    Args:
        S3UploadKeySecret in instance tags via app
        app.config["s3.policy"] pointing at a policy document

    Returns:
        Encoded policy and signature
    """
    private_key = app.config["instance.tags"]["S3UploadKeySecret"]

    policy = ''
    try:
        with open(app.config["s3.policy"]) as form_file:
            policy = template(form_file.read(), vals)
    except IOError as e:
        print("[ERROR] Failed to open policy document I/O error({0}): {1}".format(e.errno, e.strerror))
        logging.error("Failed to open policy document I/O error({0}): {1}".format(e.errno, e.strerror))
        exit(0)

    policy_encoded = base64.b64encode(policy)
    signature = base64.b64encode(hmac.new(private_key, policy_encoded, sha).digest())
    return (policy_encoded, signature)


##################################################################################
# Tests
##################################################################################
def test_file_size():
    print file_size_human(0)
    print file_size_human(455)
    print file_size_human(1005)
    print file_size_human(102405)
    print file_size_human(1024005)
    print file_size_human(44232024005)

if __name__ == "__main__":
    test_file_size()
    
    

    
