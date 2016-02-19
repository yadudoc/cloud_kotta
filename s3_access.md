#How-To : Access S3 from Login machines

To access the S3 bucket associated with Turingcompute, first get a set of IAM keys.
This is generally a file which contains your username, access key id and Secret access key.

## Configure

In order to avoid specifying the keys for every access, configure the aws cli tools to use
your keys: For general use, the aws configure command is the fastest way to setup your
AWS CLI installation. Eg:

```
$ aws configure
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-west-2
Default output format [None]: json
```

Once you've done this, you can access the S3 buckets:

Here are some examples :

## Copying a local file to S3
The following cp command copies a single file to a specified bucket and key:
```
aws s3 cp test.txt s3://mybucket/test2.txt
```

## Copying a file from S3 to S3

The following cp command copies a single s3 object to a specified bucket and key:
```
aws s3 cp s3://mybucket/test.txt s3://mybucket/test2.txt
```

## Copying an S3 object to a local file

The following cp command copies a single object to a specified file locally:
```
aws s3 cp s3://mybucket/test.txt test2.txt
```
## Recursively copying S3 objects to a local directory

When passed with the parameter --recursive, the following cp command recursively copies all objects under a specified prefix and bucket to a specified directory. In this example, the bucket \
mybucket has the objects test1.txt and test2.txt:
```
aws s3 cp s3://mybucket . --recursive
```
