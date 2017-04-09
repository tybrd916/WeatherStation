#!/bin/bash

sleeptest=1
sleeptime=120 #seconds
kidname=alex.png
tmp_image="/mnt/us/extensions/tyler/$kidname"
returnval=0
newState=""
currentState=""

getImageUrl(){	
	batterypercent=$(powerd_test -s|grep "Battery Level"|cut -d " " -f 3|cut -d "%" -f 1)
	url="http://terrylane.hopto.org:8080/$kidname?batterylevel=$batterypercent"
	echo $url
}

currentTime() {
	date +%s
}

wifienable() {
	date >> /mnt/us/kindle-display.log
	echo "wifienable" >> /mnt/us/kindle-display.log
	#lipc-set-prop com.lab126.cmd wirelessEnable 1
}
wifidisable() {
	echo "wifidisable" >> /mnt/us/kindle-display.log
	#lipc-set-prop com.lab126.cmd wirelessEnable 0
}
sleepfor2() {
        /usr/bin/rtcwake -s $1
}
sleepfor() {
	#lipc-set-prop com.lab126.powerd deferSuspend 3000000
 	ENDWAIT=$(( $(currentTime) + $1 ))
 	date >> /mnt/us/kindle-display.log
	echo "set sleep for $1 seconds" >> /mnt/us/kindle-display.log
	#echo $ENDWAIT > /sys/class/rtc/rtc0/wakealarm
	lipc-set-prop -i com.lab126.powerd rtcWakeup $ENDWAIT >> /mnt/us/kindle-display.log 2>&1
    sleeptest=$?
	date >> /mnt/us/kindle-display.log
	echo "sleeptest return $sleeptest" >> /mnt/us/kindle-display.log
	while [[ $sleeptest -gt 0 ]] ;
	do
		lipc-set-prop -i com.lab126.powerd wakeUp $ENDWAIT >> /mnt/us/kindle-display.log 2>&1
		sleeptest=$?
		echo "sleeptest return $sleeptest" >> /mnt/us/kindle-display.log
		if [[ $sleeptest -gt 0 ]] ; then
		  date >> /mnt/us/kindle-display.log
		  echo "sleeptest return $?" >> /mnt/us/kindle-display.log
		fi
	done
}

wait_for_wifi() {
	echo "wait_for_wifi" >> /mnt/us/kindle-display.log
	return `lipc-get-prop com.lab126.wifid cmState | grep CONNECTED | wc -l`; #return true if keyword not found
}
wait_for_ready_suspend() {
	return `powerd_test -s | grep Ready | wc -l`;
}
wait_for_screen_saver() {
	return `powerd_test -s | grep -i "screen saver" | wc -l`;
}
wait_for_state_change() {
	newState=`powerd_test -s|grep "Powerd state: "|tr -s " "|cut -d " " -f 3-`
	if [[ "$newState" != "$currentState" ]] ; then
		date >> /mnt/us/kindle-display.log
		echo "State Changed from $currentState to $newState" >> /mnt/us/kindle-display.log
		currentState="$newState"
		return 1
	else
		return 0
	fi
}

script_self_update(){
	curl http://terrylane.hopto.org:8080/static/kindle-display.sh > /mnt/us/extensions/tyler/newscript
	newmd5=$(md5sum /mnt/us/extensions/tyler/newscript|cut -d " " -f1)
	oldmd5=$(md5sum /mnt/us/extensions/tyler/kindle-display.sh|cut -d " " -f1)
	if [[ "$newmd5" != "$oldmd5" ]] ; then
		#Restart this script with new version
		date >> /mnt/us/kindle-display.log
		echo "Restart kindle-display.sh new version ($oldmd5 vs $newmd5)" >> /mnt/us/kindle-display.log
		mv /mnt/us/extensions/tyler/newscript /mnt/us/extensions/kindle-display.sh
		/mnt/us/extensions/tyler/tylerd -f &
		exit 0;
	fi
}

screen_saver_update(){
	script_self_update
	date >> /mnt/us/kindle-display.log
	echo "get $kidname in state ($currentState)" >> /mnt/us/kindle-display.log
	curl $(getImageUrl) > $tmp_image 2>/dev/null
	## 2>> /mnt/us/kindle-display.log
	/mnt/us/extensions/tyler/setscreensaver.sh $kidname
	#wget -O $tmp_image $url
	if [[ "$currentState" == "Screen Saver" ]] ; then
		eips -g /mnt/us/extensions/tyler/$kidname
	fi
}

while true;
do
	while wait_for_state_change; do sleep 1; done
#	sleepflag=$(cat /mnt/us/extensions/tyler/sleepflag)
#	if [[ "$sleepflag" == "1" ]] ; then
#		echo "woke from suspend sleepflag 1" >> /mnt/us/kindle-display.log
#	 	echo "0" > /mnt/us/extensions/tyler/sleepflag
#		while wait_for_wifi; do sleep 5; done
#		screen_saver_update
#		powerd_test -p
#	fi

	if [[ "$currentState" == "Active" || "$currentState" == "Screen Saver" ]] ; then
		wifienable
		while wait_for_wifi; do sleep 2; done
		screen_saver_update
	elif [[ "$currentState" == "Ready to suspend" ]] ; then
		date >> /mnt/us/kindle-display.log
		echo "wait for suspend" >> /mnt/us/kindle-display.log
		while wait_for_ready_suspend; do sleep 3; done
            	##lipc-set-prop -i com.lab126.powerd rtcWakeup 60 >> /mnt/us/kindle-display.log 2>&1
		echo "1" > /mnt/us/extensions/tyler/sleepflag
		sleepfor $sleeptime
	fi
done
