# app.py
from flask import Flask, render_template
from flask import request
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import datetime
import StringIO
import base64

app = Flask(__name__)


@app.route("/")
def index():
    city = 'Palo Alto'

    current_weather = getCurrentWeatherJSON(city)
    forecast = getForecastJSON(city)

    plot_url = plot_five_day_forecast(forecast)

    country = forecast['city']['country']
    temp = current_weather['main']['temp']
    description = current_weather['weather'][0]['description']
    icon = current_weather['weather'][0]['icon']

    return render_template('forecast.html', city=city.title(), country=country, temp=temp, description=description.title(), icon=icon, plot_url=plot_url)


@app.route("/forecast")
def weather_forecast():
    city = request.args.get('city')

    current_weather = getCurrentWeatherJSON(city)
    if current_weather == '404':
        return render_template('not_found.html')
    forecast = getForecastJSON(city)
    if forecast == '404':
        return render_template('not_found.html')

    plot_url = plot_five_day_forecast(forecast)

    country = forecast['city']['country']
    temp = current_weather['main']['temp']
    description = current_weather['weather'][0]['description']
    icon = current_weather['weather'][0]['icon']

    return render_template('forecast.html', city=city.title(), country=country, temp=temp, description=description.title(), icon=icon, plot_url=plot_url)


def getCurrentWeatherJSON(city):
    weather_params = {'q': city,
              'APPID': '2d9e3733495f56e1c8211e003b575e7d',
              'units': 'Imperial'
              }
    res = requests.get('http://api.openweathermap.org/data/2.5/weather', params=weather_params)
    if res.json()['cod'] == '404':
        return '404'
    return res.json()


def getForecastJSON(city):
    forecast_params = {'q': city,
              'APPID': '2d9e3733495f56e1c8211e003b575e7d',
              'units': 'Imperial'
              }
    res = requests.get('http://api.openweathermap.org/data/2.5/forecast', params=forecast_params)
    if res.json()['cod'] == '404':
        return '404'
    return res.json()


def plot_five_day_forecast(forecast):
    x = list()
    y = list()

    fig, ax = plt.subplots()

    for date in forecast['list']:
        x.append(datetime.datetime.strptime(date['dt_txt'], "%Y-%m-%d %H:%M:%S"))
        y.append(int(date['main']['temp']))

    days = mdates.DayLocator()
    ax.xaxis.set_major_locator(days)

    dayMonthFmt = mdates.DateFormatter('%d %b')
    ax.xaxis.set_major_formatter(dayMonthFmt)

    ax.plot(x, y)
    plt.yticks(np.arange(min(y) - 6, max(y) + 6, 6.0))
    plt.ylabel('Temp(' + u'\xb0' + 'F)')
    plt.grid()

    img = StringIO.StringIO()
    plt.savefig(img, format='png')
    img.seek(0)

    plot_url = base64.b64encode(img.getvalue())

    return plot_url


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return "500 error"

if __name__ == "__main__":
    app.debug = True
    app.run(port=33507)