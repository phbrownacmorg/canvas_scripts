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
STATDIR=/home/phbrown/bin/canvas_scripts
STATFILE=${STATDIR}/converse.instructure.com-upload.txt
FILE_CONTENTS=`/usr/bin/head --bytes=100 $STATFILE`
#echo FILE_CONTENTS is "$FILE_CONTENTS"
ALL_DIGITS="$(expr "$FILE_CONTENTS" : '^[0-9]\+$')"
#echo ALL_DIGITS is "$ALL_DIGITS"
MODTIME=`/bin/date  --reference=$STATFILE +%s`
#echo Modtime: $MODTIME
AGE=$((`/bin/date +%s` - $MODTIME))
#echo age = $AGE

# Check for stale input data.
# This will warn if *any* input file is stale (older than the threshold)
# and return critical if *all* the input files are stale.
INPUTDIR=/mnt/Canvas_Data
# 15 hours.  No update from 8 PM - 7 AM shouldn't cause an alarm.
STALE_INPUT_THRESHOLD=54000
OLDEST_INPUT=0
NEWEST_INPUT=86500000  # 1000 days.  Assume no input file is older than this.
for f in $INPUTDIR/*.csv ; do
    echo $f
    # Exclude accounts.csv (which is manually generated) from age-checking
    if [ "$f" == "${INPUTDIR}/accounts.csv" ] ; then
	    continue
    fi
    INPUT_MOD=`/bin/date  --reference=$f +%s`
    #echo $INPUT_MOD
    THIS_AGE=$((`/bin/date +%s` - $INPUT_MOD))
    #echo $THIS_AGE
    if [ $THIS_AGE -lt $NEWEST_INPUT ]; then
	    NEWEST_INPUT=$THIS_AGE
    fi
    if [ $THIS_AGE -gt $OLDEST_INPUT ]; then
	    OLDEST_INPUT=$THIS_AGE
    fi
    #echo $OLDEST_INPUT
done


if [ $NEWEST_INPUT -gt $STALE_INPUT_THRESHOLD ]; then
    echo "CRITICAL - Newest input file is aged $NEWEST_INPUT sec"
    exit $STATE_CRITICAL
elif [ $OLDEST_INPUT -gt $STALE_INPUT_THRESHOLD ]; then
    echo "WARN - Stale input file aged $OLDEST_INPUT sec"
    exit $STATE_WARNING
elif [ "$ALL_DIGITS" != "0" ]; then
    echo "OK - Last upload was $FILE_CONTENTS"
    exit $STATE_OK;
elif [ $AGE -gt $CRIT ]; then
    echo "WARN - $FILE_CONTENTS - for $AGE sec"
    exit $STATE_WARNING
else
    ${STATDIR}/autofix.py &
    echo "CRITICAL - $FILE_CONTENTS"
    exit $STATE_CRITICAL
fi
