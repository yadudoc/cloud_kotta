#!/bin/bash

CPU_LOAD=$(uptime | awk 'BEGIN{ OFS=" " } {print $(NF-2), $(NF-1), $(NF)}')
MEM_LOAD=$(free -m | grep "Mem:" | awk 'BEGIN{ OFS=", " } {print $2, $3, $4}')

echo "{\"cpu\" : \"$CPU_LOAD\", \"mem\" : \"$MEM_LOAD\"}"

