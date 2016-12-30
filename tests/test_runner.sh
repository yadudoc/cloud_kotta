#!/bin/bash

MACHINES=$1
COUNT=$2

if [[ "$MACHINES" -eq "" ]]
then
    echo "Need num machines and count"
    exit 0
fi

if [[ "$COUNT" -eq "" ]]
then
    echo "Need num machines and count"
    exit 0
fi

LOG="auto_tput_10K_$1minmax.log"
./throughput_test.py -j job_definitions.py -r submit -t $COUNT &> $LOG
sleep 600
./delete_items_by_jobname.py tput_test_10000_Test_0s           &> $LOG.analysis
./analyzer.sh $LOG.analysis

#aws autoscaling --region us-east-1 update-auto-scaling-group --auto-scaling-group-name Turing2-0-TestAutoScaling-12DULCQF569TI --min-size 8 --max-size 8 --desired-capacity 8
