#!/bin/bash

imagename="familypicture.png"
if [[ $# -gt 0 ]] ; then
  imagename=$1
fi

#Check for adunits Amazon update to turn back off
touch /var/local/adunits/test.sh 2>/dev/null
addir=$?
if [[ $addir -eq 0 ]] ; then
  date >> /mnt/us/setscreensaver.log
  echo "Amazon updated adunits, need to reset" >> /mnt/us/setscreensaver.log
  stop framework
  rm -rf /var/local/adunits.bak
  mv /var/local/adunits /var/local/adunits.bak
  touch /var/local/adunits
  chmod 000 /var/local/adunits
  start framework
fi

#/mnt/us/extensions/tyler/downloadweatherdata.sh 0ee0109ce52c6248

#check if screensaver image size has changed
destsize=`md5sum /usr/share/blanket/screensaver/bg_xsmall_ss00.png|cut -d" " -f 1`
targetsize=`md5sum /mnt/us/extensions/tyler/$imagename|cut -d" " -f 1`
if [[ "$destsize" != "$targetsize" ]] ; then
  #echo "different md5s refresh file"
  echo "md5sum difference ... Updating screen saver image" >> /mnt/us/setscreensaver.log
  ls /usr/share/blanket/screensaver/*png|sed "s/^/cp \/mnt\/us\/extensions\/tyler\/$imagename /g" > /mnt/us/extensions/tyler/screensvrcp.sh
  chmod 777 /mnt/us/extensions/tyler/screensvrcp.sh
  /mnt/us/extensions/tyler/screensvrcp.sh
fi

#Check if static screensavers have been refreshed from Amazon
screensvrsizecount=`ls -ltr /usr/share/blanket/screensaver/*png|tr -s " "|cut -d" " -f 5|sort |uniq -c|wc -l`
if [[ $screensvrsizecount -gt 1 ]] ; then
  date >> /mnt/us/setscreensaver.log
  echo "Amazon updated static screensavers, need to reset" >> /mnt/us/setscreensaver.log
  ls /usr/share/blanket/screensaver/*png|sed "s/^/cp \/mnt\/us\/extensions\/tyler\/$imagename /g" > /mnt/us/extensions/tyler/screensvrcp.sh
  chmod 777 /mnt/us/extensions/tyler/screensvrcp.sh
  /mnt/us/extensions/tyler/screensvrcp.sh
fi