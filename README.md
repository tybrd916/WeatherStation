This WeatherStation project was inspired by http://hackaday.com/2012/09/17/turning-a-kindle-into-a-weather-display/ with a slightly different angle in that I wanted my young son and daughter to get a visual cue for how to dress (or bundle up) based on the weather forecast.

Then it morphed a little when I added an infographic chart of the hourly temperatures and precipitation forecast for the next 3 days and nights.

Kindle shortcuts to enable usbnet:
* touch - search for ;un
* older - ;debugOn ;un

### Crontab entry:
- `vi /etc/crontab/root`
- `*/1 * * * * /mnt/us/extensions/tyler/tylerd`
- restart kindle

### Random notes about j a i l b r e a k for Kindle Keyboard K3W to install this weather display
https://www.turnkeylinux.org/blog/kindle-root
;debugOn --> ~usbNetwork

### Random notes about Kindle 4 NT (Non-Touch)
https://wiki.mobileread.com/wiki/Kindle4NTHacking#Jailbreak


### Notes about waking Kindle more frequently to update weather
3/13/2014 peterson:
https://www.mobileread.com/forums/showthread.php?t=235821
