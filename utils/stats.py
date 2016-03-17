import boto.ec2.cloudwatch

c  = c = boto.ec2.cloudwatch.connect_to_region('us-west-2')
metrics = c.list_metrics()
metrics
