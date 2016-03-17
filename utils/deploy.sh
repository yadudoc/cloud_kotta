#!/bin/bash

NCSES='/home/ubuntu/ncses'
TARGET='s3://klab-jobs/inputs/yadu/software/'
TAR_BALL="ncses.tar.gz"


cd $(dirname $NCSES)
rm -f $TAR_BALL

tar -czf $TAR_BALL $(basename $NCSES)
aws s3 cp --region us-east-1 $TAR_BALL "$TARGET$TAR_BALL"

rm -f $TAR_BALL


