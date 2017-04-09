#!/bin/bash

if [[ "$1" == "-f" ]] ; then
        pidToKill=`ps -ef|grep kindle-display.sh|tr -s " "|grep " 1 "|cut -d " " -f 2`
        if [[ $pidToKill -gt 0 ]] ; then
                kill -9 $pidToKill
                sleep 3
        fi
fi

isrunning=`ps -ef|grep kindle-display.sh|grep " 1 "|wc -l`
if [[ $isrunning -le 0 ]] ; then
  if [[ -f /mnt/us/extensions/tyler/newscript ]] ; then
    mv /mnt/us/extensions/tyler/newscript /mnt/us/extensions/tyler/kindle-display.sh
  fi                                          
  /mnt/us/extensions/tyler/kindle-display.sh &
fi
