#!/bin/bash


COUNT=10000
WAIT_DUR=
for machines in 16 8 4 2 1
do
    echo "Scaling to $machines"
    #aws autoscaling --region us-east-1 update-auto-scaling-group --auto-scaling-group-name Turing2-0-TestAutoScaling-12DULCQF569TI --min-size $machines --max-size $machines --desired-capacity $machines
    #sleep 600
    for i in $(seq 1 1 $ITER)
    do
	echo "Running iteration $i on Machines: $machines"
	LOG="auto_tput_10K_count$machines_iter_$i.log"

	#./throughput_test.py -j job_definitions.py -r submit -t $COUNT &> $LOG
	#sleep 600
	#./delete_items_by_jobname.py tput_test_10000_Test_0s           &> $LOG.analysis
	#./analyzer.sh $LOG.analysis
    done   
done
