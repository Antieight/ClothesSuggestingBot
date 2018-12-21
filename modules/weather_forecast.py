import sys; sys.path.insert(0, '..')

import requests as re
from bs4 import BeautifulSoup
from functools import lru_cache

from objects.weather_forecast import *
from typing import Tuple, List, Optional


@lru_cache(maxsize=128)
def _cached_get_refined_city_and_its_page_html(place: str, date: datetime.date) -> Tuple[str, str]:
    """ returns refined city name and its page html, takes place - string and date - datetime.date """

    weather_page_url = 'http://yandex.ru/pogoda/search?request={}'.format(place)
    weather_page_response = re.get(weather_page_url)
    weather_page_html = weather_page_response.text

    # if this city is not unique (which is usually the case), we should also choose the most popular one: 
    # all options are stored in options variable and can be returned as well
    options = [place]
    if 'search?request' in weather_page_response.url:
        options_bs =  BeautifulSoup(weather_page_html, 'lxml').find_all('a', class_='place-list__item-name')    
        url = 'http://yandex.ru' + options_bs[0].attrs['href']
        options = [x.next for x in options_bs]
        weather_page_response = re.get(url)
        weather_page_html = weather_page_response.text

    further_link = BeautifulSoup(weather_page_html, 'lxml').find('div', class_='forecast-briefly-old__day').a['href']
    weather_page_url = 'http://yandex.ru' + further_link
    weather_page_response = re.get(weather_page_url)
    weather_page_html = weather_page_response.text

    return options[0], weather_page_html


def get_refined_city_name_and_its_page_html(place: str) -> Tuple[str, str]:
    """ returns the refined city_name and its page html, wraps the cached version"""
    today = (datetime.datetime.utcnow() + datetime.timedelta(3/24)).date()
    return _cached_get_refined_city_and_its_page_html(place, today)


def get_weather_dict(place: str, dates: Optional[List[datetime.date]] = None) -> dict:
    """ 
        gets some raw data with weather_forecast
        place - city_name, for which we want the weather forecast
        dates is a list (or any other iterable) of dates, for which we want the weather forecast

        returns a dict, that stores the weather forecast. It is organized as follows:
        {
            'place': 'city_name', 
            date1: {
                'place': 'city_name',
                'date': date1
                'утро':{
                    'place': 'city_name',
                    'date': date1,
                    'daytime_id': daytime_id,
                    'temperature': ..,
                    ...
                },
                'день': {
                    ...
                },
                ...
                'ночь': {
                    ...
                }
            },
            date2: {
                ...
            },
            ...
            date_n: { ... }
        }
    """
    today = (datetime.datetime.utcnow() + datetime.timedelta(3/24)).date()
    if dates is None:
        dates = [today]
    city_name, weather_page_html = get_refined_city_name_and_its_page_html(place)

    weather_forecast = {'place': city_name}
    for date in dates:
        # for each date we read the day_forecast
        b = BeautifulSoup(weather_page_html, 'lxml').find_all('dt', attrs={'data-anchor':date.day})[0]
        while b.name != 'dd':
            b = b.next
        this_day_tag = b

        trs = this_day_tag.table.tbody.find_all('tr')
        weather_by_daytime = {'place': city_name, 'date': date}
        for i, tr in enumerate(trs):
            # now for each daytime we need the forecast_frame (again, in raw form)
            tds = tr.find_all('td')
            cur_weather = {'place': city_name, 'date': date, 'daytime_id': DAYTIME_IDS[i]}

            temps = tds[0].find_all('span', class_='temp__value')
            cur_weather['temperature'] = tuple(map(lambda x: x.next, temps))
            if len(cur_weather['temperature']) == 1:
                cur_weather['temperature'] = (cur_weather['temperature'][0], cur_weather['temperature'][0])

            cur_weather['condition'] = tds[2].next

            cur_weather['air_pressure'] = tds[3].next

            cur_weather['humidity_percentage'] = tds[4].next
            
            if tds[5].find('span', class_='wind-speed'):
                cur_weather['wind_strength'] = tds[5].find_all('span', class_='wind-speed')[0].next
                cur_weather['wind_direction'] = tds[5].find_all('abbr')[0]['title']
            else:
                cur_weather['wind_strength'] = 0
                cur_weather['wind_direction'] = None

            if 'wind_direction' in cur_weather and cur_weather['wind_direction'] is not None:
                cur_weather['wind_direction'] = cur_weather['wind_direction'][7:].split('-')
                cur_weather['wind_direction'] = ''.join(map(lambda x: x[0].upper(), cur_weather['wind_direction']))
            
            cur_weather['feels_like'] = tds[6].find('span', class_='temp__value').text
            weather_by_daytime[DAYTIME_NAMES[i]] = cur_weather

        if b.find('dl', class_='forecast-fields'):
            forecast_fields = list(b.find('dl', class_='forecast-fields').children)
            fields_names = list(map(lambda x:x.next, forecast_fields[::2]))
            fields = forecast_fields[1::2]
            for i in range(len(fields)):
                fields[i] = fields[i].next if i != 0 else fields[i].next + fields[i].next.next.text
            for n, f in zip(fields_names, fields):
                weather_by_daytime[n] = f
        
        try:
            sunrise_sunset_values = b.find_all('dd', class_='sunrise-sunset__value')
            weather_by_daytime['sunrise'] = datetime.datetime.strptime(sunrise_sunset_values[0].next, '%H:%M').time()
            weather_by_daytime['sunset'] = datetime.datetime.strptime(sunrise_sunset_values[1].next, '%H:%M').time()
            weather_by_daytime['duration'] = sunrise_sunset_values[2].next.replace('\xa0','')
        except Exception:  # happens, when city does not have sunset/sunrise (polar day/night)
            pass
        weather_forecast[date] = weather_by_daytime
    return weather_forecast


def fill_weather_forecast(weather_forecast: WeatherForecast) -> WeatherForecast:
    """
    Accepts the weather_forecast that is ready for prediction and
    fills it up with the weather forecast. The weather_forecast is changed as well
    :param weather_forecast: the WeatherForecast object, that is ready for prediction (assert)
    :return: WeatherForecast object, that stores the prediction
    """
    assert isinstance(weather_forecast, WeatherForecast)
    assert weather_forecast.is_ready_for_prediction()

    weather_dict = get_weather_dict(weather_forecast.place, weather_forecast.get_dates())

    # refining the place..
    weather_forecast.set_place(weather_dict['place'])

    for date in weather_forecast.get_dates():
        day_forecast = weather_forecast[date]
        day_forecast_dict = weather_dict[date]
        for daytime_name in DAYTIME_NAMES:
            forecast_frame = day_forecast[daytime_name]
            forecast_frame_dict = day_forecast_dict[daytime_name]

            temperature = forecast_frame_dict['temperature']
            temperature = tuple(map(lambda s: int(s.replace('−', '-')), temperature))
            forecast_frame.set_temperature(temperature)

            feels_like = forecast_frame_dict['feels_like']
            feels_like = int(feels_like.replace('−', '-'))
            forecast_frame.set_feels_like(feels_like)

            humidity_percentage = forecast_frame_dict['humidity_percentage']
            if humidity_percentage[-1] == '%':
                humidity_percentage = humidity_percentage[:-1]
            humidity_percentage = int(humidity_percentage)
            forecast_frame.set_humidity_percentage(humidity_percentage)

            air_pressure = forecast_frame_dict['air_pressure']
            forecast_frame.set_air_pressure(int(air_pressure))

            common_state = forecast_frame_dict['condition']
            forecast_frame.set_common_state(common_state)

            wind_strength = forecast_frame_dict['wind_strength']
            wind_strength = float(wind_strength.replace(',', '.'))
            forecast_frame.set_wind_speed(wind_strength)

            wind_direction = forecast_frame_dict['wind_direction']
            forecast_frame.set_wind_direction(wind_direction)
    assert weather_forecast.stores_prediction()
    return weather_forecast


def get_weather_forecast(place: str, dates: Iterable[datetime.date]) -> WeatherForecast:
    """
    Gets the weather forecast from the web.
    :param place: Place is the name of city, for which we need the forecast
    :param dates: dates is a list of datetime.date: for which dates we need a forecast
    :return: a WeatherForecast object, that stores the prediction
    """
    weather_forecast = WeatherForecast(place=place, dates=dates)
    fill_weather_forecast(weather_forecast)
    return weather_forecast
