#!/bin/bash

TIME=$1
CPU_LOAD=$(uptime | awk 'BEGIN{ OFS=" " } {print $(NF-2), $(NF-1), $(NF)}')
MEM_LOAD=$(free -m | grep "Mem:" | awk 'BEGIN{ OFS=", " } {print $2, $3, $4}')
DISK_LOAD=$(iostat | grep "xvda"  | awk '{sum_read+=$3; sum_write+=$4} END {print sum_read", "sum_write}')
echo "{\"time\":\"$TIME\", \"cpu\" : \"$CPU_LOAD\", \"mem\" : \"$MEM_LOAD\", \"disk\" : \"$DISK_LOAD\" }"

