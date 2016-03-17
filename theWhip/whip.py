#!/usr/bin/env python

import boto.ec2.autoscale
import boto.ec2.cloudwatch

def monitor(app):
    return True


def init(app):
    regions = ['us-east-1']
    cloudwatch = {}
    for r in regions:
        cloudwatch[r] = boto.ec2.cloudwatch.connect_to_region(r)
    
