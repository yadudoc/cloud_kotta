#!/bin/bash

run(){
    machines=$1
    sleeptime=$2
    aws autoscaling --region us-east-1 update-auto-scaling-group --auto-scaling-group-name Turing2-0-TestAutoScaling-12DULCQF569TI --min-size $machines --max-size $machines --desired-capacity $machines
    echo "Scaling to $machines sleeping $sleeptime"
    sleep 120
    LOG="auto_tput_10K_$machines-minmax.log"
    ./throughput_test.py -j job_definitions.py -r submit -t 10000 &> $LOG
    sleep $sleeptime
    ./delete_items_by_jobname.py tput_test_10000_Test_0s          &> $LOG.analysis
    ./analyzer.sh $LOG.analysis
    
}

#run 2 1250
#run 1 2000
#sleep 300
run 32 600
