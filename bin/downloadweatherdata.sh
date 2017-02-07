#!/bin/bash
apikey=$1
refreshflag=1

if [[ -f "conditions.json" ]] ; then
  refreshflag=`find conditions.json -mmin +60|wc -l`
fi

if [[ $refreshflag -gt 0 ]] ; then
  curl http://api.wunderground.com/api/$apikey/geolookup/hourly10day/q/VT/Williston.json > hourly10day.json
  curl http://api.wunderground.com/api/$apikey/geolookup/conditions/q/VT/Williston.json > conditions.json

  python bin/weatherpng.py

  scp base_marked.png root@8.0.0.22:/mnt/us/extensions/tyler/.
fi
