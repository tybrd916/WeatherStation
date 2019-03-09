#!/bin/bash
cd /home/pi/WeatherStation/
nohup python bin/app.py 8080 d299e91002f20a45070188ba289dc71a "/home/pi/" > /home/pi/WeatherStation/webpy.log &
