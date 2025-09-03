#!/bin/bash

# Nagios plugin to check on the outbound connection from w4681

. /usr/lib/nagios/plugins/utils.sh

while getopts "c:w:h" ARG; do
	case $ARG in
		#w) WARN=$OPTARG;;
		#c) CRIT=$OPTARG;;
		h) echo "Usage: $0"; exit;;
	esac
done

COUNT=`netstat -an | grep :13389 | wc -l`
# echo $COUNT listening

OUTFILE=/mnt/U/DEd/cst_state.txt

if [ "$COUNT" == "2" ]; then
    echo "OK - $COUNT listening" | tee ${OUTFILE}
    exit $STATE_OK
else
    echo "WARN - $COUNT listening" | tee ${OUTFILE}
    exit $STATE_WARNING
fi


