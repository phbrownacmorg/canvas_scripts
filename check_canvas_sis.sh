#!/bin/bash

# Nagios plugin to check whether the SIS uploads are proceeding correctly

. /usr/lib/nagios/plugins/utils.sh

# set default values for the thresholds
#WARN=90
CRIT=$((15*60))

while getopts "c:w:h" ARG; do
	case $ARG in
		#w) WARN=$OPTARG;;
		c) CRIT=$OPTARG;;
		h) echo "Usage: $0 -c <critical threshold in seconds>"; exit;;
	esac
done
#echo Crit: $CRIT
STATFILE=/home/phbrown/bin/canvas_scripts/converse.instructure.com-upload.txt
FILE_CONTENTS=`/usr/bin/head --bytes=100 $STATFILE`
#echo FILE_CONTENTS is "$FILE_CONTENTS"
ALL_DIGITS="$(expr "$FILE_CONTENTS" : '^[0-9]\+$')"
#echo ALL_DIGITS is "$ALL_DIGITS"
MODTIME=`/bin/date  --reference=$STATFILE +%s`
#echo Modtime: $MODTIME
AGE=$((`/bin/date +%s` - $MODTIME))
#echo age = $AGE

# Check for stale input data
INPUTDIR=/mnt/Canvas_Data
STALE_INPUT_THRESHOLD=7200
INPUT_AGE=0
for f in $INPUTDIR/*.csv ; do
    #echo $f
    INPUT_MOD=`/bin/date  --reference=$f +%s`
    #echo $INPUT_MOD
    THIS_AGE=$((`/bin/date +%s` - $INPUT_MOD))
    #echo $THIS_AGE
    if [ $THIS_AGE -gt $INPUT_AGE ]; then
	INPUT_AGE=$THIS_AGE
    fi
    #echo $INPUT_AGE
done


if [ $INPUT_AGE -gt $STALE_INPUT_THRESHOLD ]; then
    echo "CRITICAL - Stale input file(s) aged $INPUT_AGE sec"
    exit $STATE_CRITICAL
elif [ "$ALL_DIGITS" != "0" ]; then
    echo "OK - Last upload was $FILE_CONTENTS"
    exit $STATE_OK;
elif [ $AGE -lt $CRIT ]; then
    echo "WARN - $FILE_CONTENTS - for $AGE sec"
    exit $STATE_WARN
else
    
    echo "CRITICAL - $FILE_CONTENTS"
    exit $STATE_CRITICAL
fi
