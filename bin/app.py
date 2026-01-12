from flask import Flask, send_file, render_template, request
import time
import datetime
import pytz
import json
import requests
import re
import os
# print dir(requests)
# import requests_cache
import io
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
from PIL import ImageOps
import numpy
import sys
import matplotlib
import random
matplotlib.use("agg")
import matplotlib.pyplot as plt

workingDir='/Users/tcarr/'

if len(sys.argv) < 4:
    print("You MUST supply a port and weatherunderground API key and working directory")
    exit(2)

apikey = sys.argv[2]
workingDir= sys.argv[3]


def fig2data(fig):
    """
    @brief Convert a Matplotlib figure to a 4D numpy
    array with RGBA channels and return it
    @param fig a matplotlib figure
    @return a numpy 3D array of RGBA values
    """
    # draw the renderer
    fig.canvas.draw()

    # Get the RGBA buffer from the figure
    w, h = fig.canvas.get_width_height()
    buf = numpy.frombuffer(fig.canvas.tostring_argb(), dtype=numpy.uint8)
    buf.shape = (w, h, 4)

    # canvas.tostring_argb give pixmap in ARGB mode.
    # Roll the ALPHA channel to have it in RGBA mode
    buf = numpy.roll(buf, 3, axis=2)
    return buf

def fig2img ( fig ):
    """
    @brief Convert a Matplotlib figure to a PIL Image in RGBA format and return it
    @param fig a matplotlib figure
    @return a Python Imaging Library ( PIL ) image
    """
    # put the figure pixmap into a numpy array
    buf = fig2data ( fig )
    w, h, d = buf.shape
    return Image.frombytes( "RGBA", ( w ,h ), buf.tobytes( ) )

#requests_cache.install_cache('weatherunderground_cache', backend='sqlite', expire_after=1800)

weekday_abbrevs = [
"Sun",
"Mon",
"Tue",
"Wed",
"Thu",
"Fri",
"Sat"
]

app = Flask(__name__, template_folder='../templates')

def resolveLocation(imagename):
    returnStr="VT/Williston"
    if imagename=="/una.png":
        returnStr="FL/Sarasota"
    elif imagename=="/colorado.png":
        returnStr="CO/Louisville"
    return returnStr

def resolveLocationPrefix(imagename):
    returnStr="Williston"
    if imagename=="/una.png":
        returnStr="Sarasota"
    elif imagename=="/colorado.png":
        returnStr="LouisvilleCO"
    return returnStr

@app.route('/<imagename>.png')
@app.route('/<imagename>.gif')
@app.route('/<imagename>.bmp')
def serve_image(imagename):
    imagepath = request.path
    ext = ".png"  # name.split(".")[-1] # Gather extension
    
    if(re.compile("^.*[.]gif$").match(imagepath)):
        ext = ".gif"
    if(re.compile("^.*[.]bmp$").match(imagepath)):
        ext = ".bmp"

    cType = {
        "png":"image/png",
        "jpg":"image/jpeg",
        "gif":"image/gif",
        "ico":"image/x-icon"
    }

    downloadfreshdata=1
    now = time.time()
    #with open(str(workingDir)+'WeatherStation/hourly10day.json', 'w') as hourlyforecast10day_outfile:
    if os.path.isfile(str(workingDir)+'WeatherStation/'+resolveLocationPrefix(imagepath)+'hourly10day.json'):
        if os.stat(str(workingDir)+'WeatherStation/'+resolveLocationPrefix(imagepath)+'hourly10day.json').st_mtime > now - 3600:
            #print "file is new-ish, don't refresh!"
            downloadfreshdata=1 #0

    print("tyler sees APIKEY = "+apikey)
    if downloadfreshdata > 0 :
        hourlyforecast10day = requests.get("https://api.weather.gov/gridpoints/BTV/92,57/forecast/hourly").json()
        if len(hourlyforecast10day["properties"]["periods"]) > 0:
            with open(str(workingDir)+'WeatherStation/'+resolveLocationPrefix(imagepath)+'hourly10day.json', 'w') as hourlyforecast10day_outfile:
                json.dump(hourlyforecast10day, hourlyforecast10day_outfile,indent=1)

                weatherconditions = requests.get("https://api.weather.gov/gridpoints/BTV/92,57/forecast").json()
                with open(str(workingDir)+'WeatherStation/'+resolveLocationPrefix(imagepath)+'conditions.json', 'w') as conditions_outfile:
                    json.dump(weatherconditions, conditions_outfile,indent=1)
    else:
        with open(str(workingDir)+'WeatherStation/'+resolveLocationPrefix(imagepath)+'hourly10day.json') as json_hourlyforecast10day_data:
            hourlyforecast10day = json.load(json_hourlyforecast10day_data)
        with open(str(workingDir)+'WeatherStation/'+resolveLocationPrefix(imagepath)+'conditions.json') as json_conditions_data:
            weatherconditions = json.load(json_conditions_data)

    forecastlabel="Today"
    currhour = time.strftime("%H")
    currtime = time.strftime("%m/%d %I:%M %p")
    targetdate = datetime.datetime.strptime(time.strftime("%m/%d/%Y"),"%m/%d/%Y")
    if int(currhour) > 16:
        forecastlabel="Tomorrow"
        targetdate = targetdate + datetime.timedelta(days=1)
    targetdatestr = targetdate.strftime("%m/%d/%Y")
    currtemp = str(hourlyforecast10day["properties"]["periods"][0]["temperature"])
    targethigh = -1000;
    targetlow = 1000;
    if int(currhour) > 12 and int(currhour) < 16:
        noonhour=currhour
    else:
        noonhour=12
    noontemp=currtemp
    timelist=[]
    preciplist=[]
    templist=[]
    tz = pytz.timezone('America/New_York')
    firsthour=datetime.datetime.strftime(datetime.datetime.fromisoformat(hourlyforecast10day["properties"]["periods"][0]['startTime']),"%H")
    for i, entry in enumerate(hourlyforecast10day["properties"]["periods"]):
        hdate=datetime.datetime.strftime(datetime.datetime.fromisoformat(entry['startTime']),"%m/%d/%Y")
        if i <= 72:
            nexttime=datetime.datetime.fromisoformat(entry['startTime'])
            timelist.append(nexttime)
            preciplist.append(float(entry['probabilityOfPrecipitation']['value']))
            templist.append(float(entry['temperature']))
            #tylerfile.write("\n"+hdate+" Tyler sees time: "+str(nexttime.strftime("%Y-%m-%d %H:%M %z")+" precip chance: "+str(float(entry['precipProbability'])*100))+" temp: "+str(float(entry['temperature'])))
        if hdate == targetdatestr:
            print(hdate)
            hourlytemp = entry['temperature']
            if datetime.datetime.strftime(datetime.datetime.fromisoformat(entry['startTime']),"%H") == int(noonhour):
                noontemp=hourlytemp
            #print hourlytemp
            if float(hourlytemp) < float(targetlow):
                targetlow = hourlytemp
            if float(hourlytemp) > float(targethigh):
                targethigh = hourlytemp
    fig = plt.figure(figsize=(6.5,2), dpi=100, frameon=False)
    axTemp = fig.add_axes([0.05, 0.03, .87, 0.93])
    axTemp.plot(templist,color="black")
    axTemp.tick_params(labelsize=14)

    axPrecip = axTemp.twinx()
    y_pos = numpy.arange(len(preciplist))
    axPrecip.bar(y_pos, preciplist, align="center")
    axPrecip.set_ylim([0,100])
    
    #fig.set_size_inches(3, 1)
    axTemp.set_aspect('auto')
    axTemp.set_xlim([-1, 48])
    axTemp.set_xbound(lower=-1.0, upper=48)
    fig.autofmt_xdate()
    plotImage = fig2img(fig)
    plotImage = plotImage.convert("RGBA")
    datas = plotImage.getdata()
    
    newData = []
    for item in datas:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    print("Tyler A")
    
    plotImage.putdata(newData)
        
    kid="WeatherGirl"
    if imagepath == "/alex.png" or imagepath == "/colorado.png":
        kid="WeatherBoy"
    if (imagepath == "/una.png" or imagepath == "/tyler.png") and bool(random.getrandbits(1)):
        kid="WeatherBoy"
    clothes=5
    testtemp=noontemp
    if float(testtemp) < 35:
        clothes="_Under35.png"
    elif float(testtemp) < 50:
        clothes="_Under50.png"
    elif float(testtemp) >= 80:
        clothes="_Over80.png"
    elif float(testtemp) >= 65:
        clothes="_Over65.png"
    elif float(testtemp) >= 60:
        clothes="_Over60.png"
    elif float(testtemp) >= 50:
        clothes="_Over50.png"
    print("Tyler B")

    labelfont = ImageFont.truetype(str(workingDir)+"WeatherStation/static/FreeSans.ttf",30)
    temperaturefont = ImageFont.truetype(str(workingDir)+"WeatherStation/static/FreeSans.ttf",110)
    notefont = ImageFont.truetype(str(workingDir)+"WeatherStation/static/FreeSans.ttf",20)
    fontcolor=(0,0,0)
    degreesymbol=u"\u00b0"
    print("Tyler C")

    # Opening the file gg.png
    imageFile = str(workingDir)+"WeatherStation/static/"+kid+clothes
    print("Tyler D", imageFile)
    im1=Image.open(imageFile)
    print("Tyler E", im1)
    #http://terrylane.hopto.org:8080/helen.png
    im1.thumbnail((575,575), Image.Resampling.LANCZOS)
    print("Tyler F", im1)

    iconMap={
    "skc": "clear-day.png",
    "few": "partly-cloudy-day.png",
    "sct": "partly-cloudy-day.png",
    "bkn": "cloudy.png",
    "ovc": "cloudy.png",
    "wind_skc": "wind.png",
    "wind_few": "wind.png",
    "wind_sct": "wind.png",
    "wind_bkn": "wind.png",
    "wind_ovc": "wind.png",
    "snow": "snow.png",
    "rain_snow": "snow.png",
    "rain_sleet": "sleet.png",
    "snow_sleet": "sleet.png",
    "fzra": "rain.png",
    "rain_fzra": "rain.png",
    "snow_fzra": "rain.png",
    "sleet": "sleet.png",
    "rain": "rain.png",
    "rain_showers": "rain.png",
    "rain_showers_hi": "rain.png",
    "tsra": "rain.png",
    "tsra_sct": "rain.png",
    "tsra_hi": "rain.png",
    "tornado": "rain.png",
    "hurricane": "rain.png",
    "tropical_storm": "rain.png",
    "dust": "fog.png",
    "smoke": "fog.png",
    "haze": "fog.png",
    "hot": "clear-day.png",
    "cold": "snow.png",
    "blizzard": "snow.png",
    "fog": "fog.png",
    }

    # Opening the icon file
    iconUrl=str(weatherconditions["properties"]["periods"][0 if forecastlabel == "Today" else 1]["icon"]).split(",")[0].split("?")[0]
    iconStr=iconMap[re.sub('^.*[/]([^/]+)[,?]?.*$', r'\1',iconUrl)] 
    iconFile = str(workingDir)+"WeatherStation/static/"+iconStr
    imIcon=Image.open(iconFile)
    imIcon.thumbnail((575,575), Image.Resampling.LANCZOS)

    im2=Image.new("RGBA", (600, 800), (255,255,255))
    im4=Image.new("L", (600, 800), 255)
    draw = ImageDraw.Draw(im2)

    barwidth=11.5
    graphbackoffset=60
    weekdaysOffset=85
    dayOffset=1
    nightRectWidth=float(barwidth)*11
    dayRectWidth=float(barwidth)*13
    if int(firsthour) < 6:
        nightRectWidth = float(barwidth)*(6-int(firsthour))
        weekdaysOffset=int(weekdaysOffset+nightRectWidth)
    elif int(firsthour) > 18: #Graph Forecast starts in night-time
        nightRectWidth = float(barwidth)*(6+(24-int(firsthour)))
        weekdaysOffset=int(weekdaysOffset+nightRectWidth)
    elif int(firsthour) <= 18:
        graphbackoffset=graphbackoffset+(float(barwidth)*(18-int(firsthour)))
        weekdaysOffset=int(weekdaysOffset+(float(barwidth)*(18-int(firsthour))))+nightRectWidth
        if int(firsthour) < 16:
            dayOffset=2

    draw.rectangle((graphbackoffset,550,graphbackoffset+nightRectWidth,750),fill="#dddddd")
    graphbackoffset=graphbackoffset+nightRectWidth+dayRectWidth
    nightRectWidth=float(barwidth)*11
    draw.rectangle((graphbackoffset,550,graphbackoffset+nightRectWidth,750),fill="#dddddd")
    graphbackoffset=graphbackoffset+nightRectWidth+dayRectWidth
    nightRectWidth=float(barwidth)*11
    draw.rectangle((graphbackoffset,550,graphbackoffset+nightRectWidth,750),fill="#dddddd")
    graphbackoffset=graphbackoffset+nightRectWidth+dayRectWidth
    nightRectWidth=float(barwidth)*11
    draw.rectangle((graphbackoffset,550,graphbackoffset+nightRectWidth,750),fill="#dddddd")
    im2.paste(plotImage,(10,550), mask=plotImage) #plot debug
    im2.paste(im1,(350,0), mask=im1)
    im2.paste(imIcon,(150,350))

    #Resolve battery level if passed
    batterypercent = request.args.get('batterylevel', None)

    # Drawing the text on the picture
    #draw = ImageDraw.Draw(im1)

    labeldate1 = targetdate + datetime.timedelta(days=int(dayOffset))
    labeldate2 = targetdate + datetime.timedelta(days=int(dayOffset)+1)
    labeldate3 = targetdate + datetime.timedelta(days=int(dayOffset)+2)
    draw.text((int(weekdaysOffset)+30,750),weekday_abbrevs[labeldate1.weekday()],fontcolor,font=notefont)
    draw.text((int(weekdaysOffset+nightRectWidth+dayRectWidth)+30,750),weekday_abbrevs[labeldate2.weekday()],fontcolor,font=notefont)
    draw.text((int(weekdaysOffset+nightRectWidth+dayRectWidth+nightRectWidth+dayRectWidth)+30,750),weekday_abbrevs[labeldate3.weekday()],fontcolor,font=notefont)

    draw.text((20, 20),forecastlabel+" High",fontcolor,font=labelfont)
    draw.text((20, 50),"{:.1f}".format(targethigh)+degreesymbol+"F",fontcolor,font=temperaturefont)
    draw.text((20, 180),forecastlabel+" Low",fontcolor,font=labelfont)
    draw.text((20, 210),"{:.1f}".format(targetlow)+degreesymbol+"F",fontcolor,font=temperaturefont)
    draw.text((20, 500),weatherconditions["properties"]["periods"][0 if forecastlabel == "Today" else 1]["shortForecast"],fontcolor,font=labelfont)
    draw.text((20, 772),"last updated: "+currtime,fontcolor,font=notefont)
    if batterypercent != None:
        draw.text((450,772),"Battery: "+batterypercent+"%",fontcolor,font=notefont)
    draw = ImageDraw.Draw(im2)
    plt.close('all')

    im2 = im2.convert("L")
    if batterypercent != None and float(batterypercent) < 20:
        im2 = ImageOps.mirror(im2)
    im4.paste(im2,(0,0))
    imgByteArr = io.BytesIO()
    if ext == ".gif":
        im2.save(imgByteArr, format='GIF')
    elif ext == ".bmp":
        im2.save(imgByteArr, format='BMP')
    else:
        im2.save(imgByteArr, format='PNG')
    imgByteArr.seek(0)
    
    mimetype = cType.get(ext[1:], 'image/png')
    return send_file(imgByteArr, mimetype=mimetype)

@app.route('/helenback.html')
def helenback():
    return render_template("previewback.html", image="helen.png")

@app.route('/alexback.html')
def alexback():
    return render_template("previewback.html", image="alex.png")

@app.route('/unaback.html')
def unaback():
    return render_template("previewback.html", image="una.png")

@app.route('/tylerback.html')
def tylerback():
    return render_template("previewback.html", image="tyler.png")

@app.route('/coloradoback.html')
def coloradoback():
    return render_template("previewback.html", image="colorado.png")

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    app.run(host='0.0.0.0', port=port, debug=True)
