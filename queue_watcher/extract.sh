#!/bin/bash


START=$1
END=$2
LOG="watch.log"


BEGIN=$(grep -n "$START" watch.log | head  -n 1 | cut -d ':' -f 1)
END=$(grep -n "$END" watch.log | head  -n 1 | cut -d ':' -f 1)

echo "From $BEGIN -> $END"

#sed -n "${BEGIN},${END}p" $LOG | grep "prod"
sed -n "${BEGIN},${END}p" $LOG | grep "test"
