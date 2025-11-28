from django.shortcuts import render,redirect,HttpResponse
import requests, datetime
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

from django.conf import settings
API_KEY=settings.API_KEY

def getWeather(city):
    response=requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric")
    return response.json()

def getAqi(response):
    aqi=requests.get(f'https://api.openweathermap.org/data/2.5/air_pollution?lat={response['coord']['lat']}&lon={response['coord']['lon']}&appid={API_KEY}')
    aqi=aqi.json()
    aqi=addAqiRating(aqi)
    return aqi

def getForecast(city):
    forecast=requests.get(f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric")
    forecast=forecast.json()
    timezoneCorrection(forecast)
    return forecast

@csrf_exempt
def home(request):
    if request.method !="POST":
        return render(request,'home.html')
    city=request.POST.get('search')
    
    if not city:
        return HttpResponse()
        
    city=city.strip()
    response=getWeather(city)
    if response['cod'] == '404':
        return HttpResponse("City Not Found")

    aqi=getAqi(response)
    forecast=getForecast(city)
    temps=getMinMaxTemp(forecast)
    return render(request,'weather.html',{'city':response,'aqi':aqi,"forecast":forecast,"temps":temps})

def addAqiRating(aqi):
    match aqi['list'][0]['main']['aqi']:
        case 1:
            aqi['rating']='Good'
        case 2:
            aqi['rating']='Fair'
        case 3:
            aqi['rating']='Moderate'
        case 4:
            aqi['rating']='Poor'
        case 5:
            aqi['rating']='Very Poor'
    return aqi
    
def timezoneCorrection(forecast):
    delta=datetime.timedelta(seconds=forecast['city']['timezone'])
    for i in forecast['list']:
        utc=datetime.datetime.strptime(i['dt_txt'], '%Y-%m-%d %H:%M:%S')
        i['dt_txt']=str(utc + delta)
    return forecast

def getMinMaxTemp(forecast):
    temps=[]
    for i in range(5):
        datestr=str(datetime.date.today()+ datetime.timedelta(days=i))
        date={'min':5000,'max':-5000}
        for j in forecast['list']:
            if j['dt_txt'][:10]==datestr:
                if date['min']>j['main']['temp_min']:
                    date['min']=j['main']['temp_min']
                if date['max']<j['main']['temp_max']:
                    date['max']=j['main']['temp_max']
        temps.append(date)
    return temps