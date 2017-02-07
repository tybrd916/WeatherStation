#!/usr/bin/python
#import sys
#sys.path.append("/mnt/us/extensions/tyler/Imaging-1.1.7")
import time
import datetime
import json
import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw

with open('hourly10day.json') as json_hourlyforecast10day_data:
    hourlyforecast10day = json.load(json_hourlyforecast10day_data)

with open('conditions.json') as json_conditions_data:
    weatherconditions = json.load(json_conditions_data)

forecastlabel="Today"
currhour = time.strftime("%H")
currtime = time.strftime("%m/%d %I:%M %p")
targetdate = datetime.datetime.strptime(time.strftime("%m/%d/%Y"),"%m/%d/%Y")
if int(currhour) > 16:
  forecastlabel="Tomorrow"
  targetdate = targetdate + datetime.timedelta(days=1)
targetdatestr = targetdate.strftime("%m/%d/%Y")
currtemp = str(weatherconditions["current_observation"]["temp_f"])
targethigh = -1000;
targetlow = 1000;
for i, entry in enumerate(hourlyforecast10day["hourly_forecast"]):
  hdate = entry['FCTTIME']['mon_padded']+"/"+entry['FCTTIME']['mday_padded']+"/"+entry['FCTTIME']['year']
  if hdate == targetdatestr:
    hourlytemp = entry['temp']['english']
    #print hourlytemp
    if float(hourlytemp) < float(targetlow):
      targetlow = hourlytemp
    if float(hourlytemp) > float(targethigh):
      targethigh = hourlytemp
kid="WeatherGirl"
#if str(web.ctx.path) == "/alex":
#  kid="alex"
clothes=5
testtemp = currtemp
if int(currhour) > 16:
  if float(targetlow) < 45:
    testtemp = targetlow
  else:
    testtemp = targethigh
#print testtemp
if float(testtemp) < 35:
  clothes="_Under35.png"
elif float(testtemp) < 50:
  clothes="_Under50.png"
elif float(testtemp) >= 50:
  clothes="_Over50.png"
elif float(testtemp) >= 60:
  clothes="_Over60.png"
elif float(testtemp) >= 65:
  clothes="_Over65.png"
elif float(testtemp) >= 80:
  clothes="Over80.png"

# Loading Fonts.
# To the font you want to use.
labelfont = ImageFont.truetype("/Library/Fonts/Verdana.ttf",30)
temperaturefont = ImageFont.truetype("/Library/Fonts/Verdana Bold.ttf",110)
notefont = ImageFont.truetype("/Library/Fonts/Verdana.ttf",15)
fontcolor=(255,255,255)
degreesymbol=u"\u00b0"

# Opening the file gg.png
imageFile = "static/"+kid+clothes
im1=Image.open(imageFile)
im1.thumbnail((700,700), Image.ANTIALIAS)

im2=Image.new("RGB", (600, 800), (0,0,0))
im2.paste(im1,(300,100))

# Drawing the text on the picture
#draw = ImageDraw.Draw(im1)
draw = ImageDraw.Draw(im2)
draw.text((20, 20),"Current Temperature",fontcolor,font=labelfont)
draw.text((20, 50),currtemp+degreesymbol+"F",fontcolor,font=temperaturefont)
draw.text((20, 200),forecastlabel+" High",fontcolor,font=labelfont)
draw.text((20, 230),str(targethigh)+degreesymbol+"F",fontcolor,font=temperaturefont)
draw.text((20, 400),forecastlabel+" Temperature",fontcolor,font=labelfont)
draw.text((20, 430),str(targetlow)+degreesymbol+"F",fontcolor,font=temperaturefont)
draw.text((20, 780),"last updated: "+currtime,fontcolor,font=notefont)
draw = ImageDraw.Draw(im2)

# Save the image with a new name
im2.save("base_marked.png")
