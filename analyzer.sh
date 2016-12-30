#!/bin/bash

input=$1
log=${input%.analysis}


submit_dur=$(grep "Completed in" $log | awk '{print $3}' | sed 's/s//')
start=$(cat $input | awk '{print $5}' | grep -o '[0-9.]*' |  sort -n | head -n 1)
end=$(cat $input | awk '{print $6}'   | grep -o '[0-9.]*' |  sort -n | tail -n 1)
tasks=$(wc -l $input)
TTC=$(echo "$end - $start" | bc)

echo "tasks: $tasks total_time_to_submit: $submit_dur total_TTC: $TTC" > $input.result
