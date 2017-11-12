import web
import time
import datetime
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
matplotlib.use("agg")
import matplotlib.pyplot as plt

workingDir='/Users/tcarr/'

if len(sys.argv) < 4:
    print "You MUST supply a port and weatherunderground API key and working directory"
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
    buf = numpy.fromstring(fig.canvas.tostring_argb(), dtype=numpy.uint8)
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
    return Image.frombytes( "RGBA", ( w ,h ), buf.tostring( ) )

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

urls = (
  '/', 'Index', 
  '/alex', 'Index',
  '/helenback.html', 'helenback',
  '/alexback.html', 'alexback',
  '/alex.png', 'images',
  '/helen.png', 'images',
  '/helen.gif', 'images',
  '/helen.bmp', 'images',
  '/helen', 'Index',
  '/conditions', 'Conditions', 
  '/hourly10day', 'Hourly'
)

app = web.application(urls, globals())

render = web.template.render('templates/')

class images:
    def GET(self):
        ext = ".png"#name.split(".")[-1] # Gather extension
        
        if(re.compile("^.*[.]gif$").match(str(web.ctx.path))):
          ext = ".gif"
        if(re.compile("^.*[.]bmp$").match(str(web.ctx.path))):
          ext = ".bmp"

        cType = {
            "png":"images/png",
            "jpg":"images/jpeg",
            "gif":"images/gif",
            "ico":"images/x-icon"            }

          
        #if name in os.listdir('images'):  # Security
        if ext == ".gif":
          web.header("Content-Type", "images/gif")
        if ext == ".bmp":
          web.header("Content-Type", "images/bmp")
        else:
          web.header("Content-Type", "images/png") # Set the Header
        #return open('images/%s'%name,"rb").read() # Notice 'rb' for reading images

        downloadfreshdata=1
        now = time.time()
        #with open(str(workingDir)+'WeatherStation/hourly10day.json', 'w') as hourlyforecast10day_outfile:
        if os.path.isfile(str(workingDir)+'WeatherStation/hourly10day.json'):
          if os.stat(str(workingDir)+'WeatherStation/hourly10day.json').st_mtime > now - 3600:
            #print "file is new-ish, don't refresh!"
            downloadfreshdata=0

        print "tyler sees APIKEY = "+apikey
        if downloadfreshdata > 0 :
        	hourlyforecast10day = requests.get("http://api.wunderground.com/api/"+apikey+"/geolookup/hourly10day/q/VT/Williston.json").json()
                with open(str(workingDir)+'WeatherStation/hourly10day.json', 'w') as hourlyforecast10day_outfile:
                  json.dump(hourlyforecast10day, hourlyforecast10day_outfile)

        #with open('/Users/tcarr/WeatherStation/conditions.json') as json_conditions_data:
        #    weatherconditions = json.load(json_conditions_data)
        	weatherconditions = requests.get("http://api.wunderground.com/api/"+apikey+"/geolookup/conditions/q/VT/Williston.json").json()
                with open(str(workingDir)+'WeatherStation/conditions.json', 'w') as conditions_outfile:
                  json.dump(weatherconditions, conditions_outfile)
        else:
             with open(str(workingDir)+'WeatherStation/hourly10day.json') as json_hourlyforecast10day_data:
               hourlyforecast10day = json.load(json_hourlyforecast10day_data)
             with open(str(workingDir)+'WeatherStation/conditions.json') as json_conditions_data:
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
        if int(currhour) > 12 and int(currhour) < 16:
          noonhour=currhour
        else:
          noonhour=12
        noontemp=currtemp
        tylerfile=open(str(workingDir)+"WeatherStation/tyler.txt","w")
        timelist=[]
        epochlist=[]
        preciplist=[]
        templist=[]
        firsthour=hourlyforecast10day["hourly_forecast"][0]['FCTTIME']['hour_padded']
        for i, entry in enumerate(hourlyforecast10day["hourly_forecast"]):
          hdate = entry['FCTTIME']['mon_padded']+"/"+entry['FCTTIME']['mday_padded']+"/"+entry['FCTTIME']['year']
          if i <= 72:
            timelist.append(datetime.datetime.fromtimestamp(float(entry['FCTTIME']['epoch'])))
            epochlist.append(float(entry['FCTTIME']['epoch']))
            preciplist.append(float(entry['pop']))
            templist.append(float(entry['temp']['english']))
            #tylerfile.write("Tyler sees:\n"+datetime.datetime.fromtimestamp(float(entry['FCTTIME']['epoch'])).strftime('%c'))
            tylerfile.write("Tyler sees:\n"+str(entry))
          if hdate == targetdatestr:
            hourlytemp = entry['temp']['english']
            if int(entry['FCTTIME']['hour_padded']) == int(noonhour):
              noontemp=hourlytemp
            #print hourlytemp
            if float(hourlytemp) < float(targetlow):
              targetlow = hourlytemp
            if float(hourlytemp) > float(targethigh):
              targethigh = hourlytemp

        #time_format = '%Y-%m-%d %H:%M'
        #timelist2=[datetime.datetime.strftime(i, time_format) for i in timelist]
        #tylerfile.write(str(timelist)+"\n")
        #tylerfile.write(str(preciplist)+"\n")
        #print "Before Plot attempt"
        ##plt = None
        ##plt = matplotlib.pyplot
        #plt.plot(timelist, preciplist)
        #print "Auto Plot attempt"
        #fig = plt.gcf()
        fig = plt.figure(figsize=(6.5,2), dpi=100, frameon=False)
        axTemp = fig.add_axes([0.1, 0.05, .8, .9])
        #axPrecip.axis('off')
        axTemp.plot(templist,color="black")

        axPrecip = axTemp.twinx()
        y_pos = numpy.arange(len(preciplist))
        axPrecip.bar(y_pos, preciplist, align="center")
        axPrecip.set_ylim([0,100])
        
        #fig.set_size_inches(3, 1)
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
        
        plotImage.putdata(newData)
        
        kid="WeatherGirl"
        if str(web.ctx.path) == "/alex.png":
          kid="WeatherBoy"
        clothes=5
        testtemp=noontemp
        #testtemp = currtemp
        #if int(currhour) > 16:
        #  if float(targetlow) < 45:
        #    testtemp = targetlow
        #  else:
        #    testtemp = targethigh
        #print testtemp
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

        # Loading Fonts.
        # To the font you want to use.
        labelfont = ImageFont.truetype(str(workingDir)+"WeatherStation/static/FreeSans.ttf",30)
        temperaturefont = ImageFont.truetype(str(workingDir)+"WeatherStation/static/FreeSans.ttf",110)
        notefont = ImageFont.truetype(str(workingDir)+"WeatherStation/static/FreeSans.ttf",15)
        fontcolor=(0,0,0)
        #fontcolor=255
        degreesymbol=u"\u00b0"

        # Opening the file gg.png
        imageFile = "static/"+kid+clothes
        im1=Image.open(imageFile)
        #http://terrylane.hopto.org:8080/helen.png
        im1.thumbnail((575,575), Image.ANTIALIAS)

        im2=Image.new("RGBA", (600, 800), (255,255,255))
        im4=Image.new("L", (600, 800), 255)
        #print im2.mode+" "+im1.mode
        #im2.paste(im1,(300,100))
        #plotImage.thumbnail((200,300), Image.ANTIALIAS)
        draw = ImageDraw.Draw(im2)

        barwidth=6.5
        graphbackoffset=95
        weekdaysOffset=95
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
          dayOffset=2

        if forecastlabel=="Tomorrow":
          dayOffset=dayOffset-1

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
        im2.paste(plotImage,(5,550), mask=plotImage) #plot debug
        im2.paste(im1,(350,0), mask=im1)

        #Resolve battery level if passed
        param_data = web.input(batterylevel=None)
        batterypercent=None
        if param_data.batterylevel != None:
          batterypercent=param_data.batterylevel

        # Drawing the text on the picture
        #draw = ImageDraw.Draw(im1)

        labeldate1 = targetdate + datetime.timedelta(days=int(dayOffset))
        labeldate2 = targetdate + datetime.timedelta(days=int(dayOffset)+1)
        labeldate3 = targetdate + datetime.timedelta(days=int(dayOffset)+2)
        draw.text((int(weekdaysOffset)+30,750),weekday_abbrevs[labeldate1.weekday()],fontcolor,font=notefont)
        draw.text((int(weekdaysOffset+nightRectWidth+dayRectWidth)+30,750),weekday_abbrevs[labeldate2.weekday()],fontcolor,font=notefont)
        draw.text((int(weekdaysOffset+nightRectWidth+dayRectWidth+nightRectWidth+dayRectWidth)+30,750),weekday_abbrevs[labeldate3.weekday()],fontcolor,font=notefont)

        draw.text((20, 20),"Recent Temperature",fontcolor,font=labelfont)
        draw.text((20, 50),currtemp+degreesymbol+"F",fontcolor,font=temperaturefont)
        draw.text((20, 200),forecastlabel+" High",fontcolor,font=labelfont)
        draw.text((20, 230),str(targethigh)+degreesymbol+"F",fontcolor,font=temperaturefont)
        draw.text((20, 400),forecastlabel+" Low",fontcolor,font=labelfont)
        draw.text((20, 430),str(targetlow)+degreesymbol+"F",fontcolor,font=temperaturefont)
        draw.text((20, 780),"last updated: "+currtime,fontcolor,font=notefont)
        if batterypercent != None:
          draw.text((450,780),"Battery: "+batterypercent+"%",fontcolor,font=notefont)
        draw = ImageDraw.Draw(im2)

        im2 = im2.convert("L")
        if batterypercent != None and batterypercent < 20:
          im2 = ImageOps.mirror(im2)
        im4.paste(im2,(0,0))
        imgByteArr = io.BytesIO()
        if ext == ".gif":
          im2.save(imgByteArr, format='GIF')
        elif ext == ".bmp":
          im2.save(imgByteArr, format='BMP')
        else:
          im2.save(imgByteArr, format='PNG')
        return imgByteArr.getvalue()

        # Save the image with a new name
        #return im2
        #im2.save("base_marked.png")
        #else:
        #    raise web.notfound()

class Conditions(object):
    def GET(self):
        weatherconditions = requests.get("http://api.wunderground.com/api/"+apikey+"/geolookup/conditions/q/VT/Williston.json").json()

        return json.dumps(weatherconditions)

class Hourly(object):
    def GET(self):
        hourlyforecast10day = requests.get("http://api.wunderground.com/api/"+apikey+"/geolookup/hourly10day/q/VT/Williston.json").json()

        return json.dumps(hourlyforecast10day)

class helenback(object):
    def GET(self):
        return render.helenback()

class alexback(object):
    def GET(self):
        return render.alexback()

class Index(object):
    def GET(self):
        weatherconditions = requests.get("http://api.wunderground.com/api/"+apikey+"/geolookup/conditions/q/VT/Williston.json").json()
        hourlyforecast10day = requests.get("http://api.wunderground.com/api/"+apikey+"/geolookup/hourly10day/q/VT/Williston.json").json()

        forecastlabel="Today"
        currhour = time.strftime("%H")
        currtime = time.strftime("%I:%M %p")
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

        kid="helen"
        if str(web.ctx.path) == "/alex":
          kid="alex"
        clothes=5
        testtemp = currtemp

        if int(currhour) > 16:
          if float(targetlow) < 45:
            testtemp = targetlow
          else:
            testtemp = targethigh

        #print testtemp

        if float(testtemp) < 35:
          clothes=1
        elif float(testtemp) < 50:
          clothes=2
        elif float(testtemp) >= 50:
          clothes=3
        elif float(testtemp) >= 60:
          clothes=4
        elif float(testtemp) >= 65:
          clothes=5
        elif float(testtemp) >= 80:
          clothes=6

        return render.weatherstation(currtime,currtemp,forecastlabel,targethigh,targetlow,kid,clothes)

if __name__ == "__main__":

    app.run()
