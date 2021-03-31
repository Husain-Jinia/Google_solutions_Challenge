import joblib
from datetime import datetime, timedelta
import requests
import sklearn
import os
from Predictor.models import Predictions

HOLIDAYURL = 'https://holidayapi.com/v1/holidays'
COUNTRY = 'CN'
LAT = '39.9042'
LON = '116.4074'
HOLIDAYKEY = 'a1b022f3-cce2-4b99-9cd3-a84b2e31f93b'
WEATHERKEY = '88b7cdc97b1b6bdbf01fa35ffe779990'
WEATHERURL = 'https://api.openweathermap.org/data/2.5/onecall'



def computeForWeek():
    tod = datetime.today()
    start_of_week = tod - timedelta(days=tod.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=6)  # Sunday
    tod = start_of_week
    holidayparameters={
    "country": COUNTRY,
    "year" : 2020,
    "key" : HOLIDAYKEY,
    "month" : 1,
    "day" : 1,
    "public" : False
    }
    weatherparameters={
        "lat" : LAT,
        "lon" : LON,
        "exclude" : 'hourly,minutely,current,alerts',
        "appid" : WEATHERKEY
    }
    days={}
    average_temp=[]    

    #finding average temperature for the next 7 days
    response = requests.get(url=WEATHERURL, params=weatherparameters)
    response.raise_for_status()
    response = response.json()

    temperatures = response["daily"]
    for i in range(7):
        x = (temperatures[i]["temp"]["min"] + temperatures[i]["temp"]["max"])/2
        average_temp.append(x)

    while tod<=end_of_week:
        i=tod.weekday()
        #input needed for the model
        date=1
        average_temperature=0
        is_weekend=True
        holiday=0
        year=1

        MONTH = tod.month
        DAY = tod.day
        YEAR = tod.year

        #finding date
        date=DAY

        #finding average temperature
        average_temperature = average_temp[i]

        #finding whether day is weekend
        if tod.weekday() == 5 or tod.weekday() == 6:
            is_weekend = True
        else:
            is_weekend = False   


        #finding whether this day is a holiday or not
        #parameters["year"] = YEAR
        holidayparameters["month"] = MONTH
        holidayparameters["day"] = DAY
        response = requests.get(url=HOLIDAYURL, params=holidayparameters )
        response.raise_for_status()
        response = response.json()
        if len(response["holidays"]):
            holiday=1
        else:
            holiday=0

        #finding year
        year = YEAR

        days[i] = {}

        days[i]["date"] = date
        days[i]["average_temperature"] = average_temperature
        days[i]["is_weekend"] = is_weekend
        days[i]["holiday"] = holiday
        days[i]["year"] = year
        tod = tod + timedelta(days=1)

    predictions = loadModel(days)
    print(predictions)
    addToDB(predictions)

def loadModel(days):
    predictions=[]
    cls = joblib.load('final.sav')

    for i in range(7):
        x = cls.predict([[days[i]["year"], days[i]["date"], days[i]["holiday"], days[i]["is_weekend"], days[i]["average_temperature"]]])
        predictions.append(x.tolist()[0])
    return predictions

def addToDB(predictions):
    tod = datetime.today()
    start_of_week = tod - timedelta(days=tod.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=6)  # Sunday
    tod = start_of_week
    while tod<=end_of_week:
        i = tod.weekday()
        x = Predictions(date = tod.strftime('%d/%m/%Y'), day=tod.strftime("%A"), prediction=predictions[i])        
        x.save()
        tod = tod + timedelta(days=1) 

def readFromDB():
    tod = datetime.today()
    start_of_week = tod - timedelta(days=tod.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=6)  # Sunday
    tod=start_of_week
    result={}

    while tod<=end_of_week:
        date = tod.strftime('%d/%m/%Y')
        i=tod.weekday()
        result[i]={}
        x = Predictions.objects.get(pk=date)
        result[i]["date"] = x.date
        result[i]["day"] = x.day
        result[i]["prediction"] = x.prediction

        tod = tod + timedelta(days=1)

    return result        

def isNewUser():
    tod = datetime.today()
    queryset = Predictions.objects.filter(date=tod.strftime('%d/%m/%Y'))
    return not queryset.exists()

def computePredictions():
    tod = datetime.today()
    result={}
    if tod.weekday() == 0 or isNewUser():
        computeForWeek()
        result=readFromDB()

    else:
        result=readFromDB()
    return result

def getNameOfToday():
    tod = datetime.today()
    return tod.strftime("%A")

def getDateOfToday():
    tod = datetime.today()
    return tod.strftime('%d/%m/%Y')

def getPredictionOfToday():
    tod = datetime.today()
    date = tod.strftime('%d/%m/%Y')
    x =  Predictions.objects.get(pk=date)
    return x.prediction
