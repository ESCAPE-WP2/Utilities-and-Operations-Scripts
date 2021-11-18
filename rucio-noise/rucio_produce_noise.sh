#!/bin/bash

python3 ../cric-info-tools/list_rses_from_cric.py -o list_rses_from_cric.txt -i ../cric-info-tools/disabled_rses.txt

rses=()
while read line
do
    rses+=($line)
done < list_rses_from_cric.txt

len=${#rses[@]}

echo '* Assigning ENV Config Variables:'
FILE_SIZE=${FILE_SIZE:-100M}
RUCIO_SCOPE=${RUCIO_SCOPE:-ESCAPE_CERN_TEAM-noise}
FILE_LIFETIME=${FILE_LIFETIME:-3600}
echo '*   FILE_SIZE = '"$FILE_SIZE"''
echo '*   RUCIO_SCOPE = '"$RUCIO_SCOPE"''
echo '*   FILE_LIFETIME = '"$FILE_LIFETIME"''

upload_and_transfer () {
    for (( i=0; i<$len; i++ )); do

        if [ $1 != $i ]; then

            echo '*** ======================================================================== ***'

            RANDOM_STRING=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
            echo '*** generated random file identifier: '"$RANDOM_STRING"' ***'

            filename=/tmp/auto_uploaded_$RANDOM_STRING
            did=auto_uploaded_$RANDOM_STRING
            
            echo '*** generating '"$FILE_SIZE"' file on local storage ***'
            head -c $FILE_SIZE < /dev/urandom  > $filename
            echo '*** filename: '"$filename"''

            echo '*** uploading to rse '"${rses[$1]}"' and adding rule to rse '"${rses[$i]}"'' 
            rucio -v upload --rse ${rses[$1]} --lifetime $FILE_LIFETIME --scope $RUCIO_SCOPE $filename && rucio add-rule --lifetime $FILE_LIFETIME --activity "Functional Test" $RUCIO_SCOPE:$did 1 ${rses[$i]}

            rm -f $filename
	    fi
    done
}

echo '* RUCIO Produce Noise START * '

for (( j=0; j<$len; j++ )); do
    upload_and_transfer $j
done

echo '* RUCIO Produce Noise DONE * '