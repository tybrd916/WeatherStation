#!/bin/bash
cd /$HOME/WeatherStation/
nohup python bin/app.py 8080 d299e91002f20a45070188ba289dc71a "$HOME/" > $HOME/WeatherStation/webpy.log &
