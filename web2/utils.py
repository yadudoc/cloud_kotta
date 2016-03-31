#!/usr/bin/env python
import math
import bottle
from bottle import template
from bottle import route, get, post, request, hook, redirect

#################################################################################
# Some global vars
#################################################################################
JobTypes = ["doc_to_vec", "script"]

##################################################################################
# Helper function to ensure that the user is logged in
##################################################################################
def require_login(session):
    if not session:
        redirect("/login")
    if session.get("logged_in") != True:
        redirect("/login")

##################################################################################
# Convert file size to human friendly
##################################################################################
def file_size_human(size):
    if size == 0 :
        return "0 B"
    suffix = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']
    index  = int(math.log(size, 1024))
    val    = size / math.pow(1024,index)
    return "{0:.2f} {1}".format(val, suffix[index])


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
    
    

    
