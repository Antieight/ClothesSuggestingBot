import sys; sys.path.insert(0, '../..')

from objects.context import Context
from modules.common_extractors import *
from modules.weather_forecast import fill_weather_forecast
from objects.request_objects import *
from objects.response_objects import *
from objects.weather_forecast import WeatherForecast
from typing import List


def parse_message(message: str, context: Context) -> Optional[List[RequestObject]]:
    """
    Takes a message and a context and extracts a list of request objects.
    :param message: the message to extract from
    :param context: the current context to look at
    :return: a list of request objects
    """
    assert isinstance(message, str)
    assert isinstance(context, Context)

    try:
        # checking for context change:
        if (context.safe_access('place') is not None and
                context.safe_access('date') is not None and
                'а' not in message.lower().split()[:2]):
            if extract_approval(message):
                return [ApproveAndStop()]
            return None

        if context.get_info()['state'] == 'initial':
            date = extract_date(message)
            place = extract_place(message)
            if date is None and place is None:
                return None
            if place is None and date is not None:
                return [RefineDate(date=date)]
            elif place is not None and date is None:
                return [RefinePlace(place=extract_place(message))]
            else:
                return [WeatherRequest(place=extract_place(message),
                                       date=extract_date(message))]
        else:
            return None
    except Exception:
        return None


def process_request_object(request_object: RequestObject, context: Context) -> List[ResponseObject]:
    """
    Takes a request object and a context and reacts to this message.
    That is changes its context and generates some response objects in return
    :param request_object:  request_object to parse
    :param context: current context of the user
    :return: a list of response objects, generated in response to the given request object
    """
    response_objects = []

    # updating the context
    if isinstance(request_object, (WeatherRequest, RefinePlace)):
        context.set_info_field('place', request_object.place)
    if isinstance(request_object, (WeatherRequest, RefineDate)):
        context.set_info_field('date', request_object.date)
    if isinstance(request_object, ApproveAndStop):
        context.reset()
        context.save()
        return [CommonMessage(':)')]
    context.save()

    if context.safe_access('place') is not None and context.safe_access('date') is not None:
        weather_forecast = WeatherForecast(place=context.safe_access('place'), dates=[context.safe_access('date')])
        weather_forecast = fill_weather_forecast(weather_forecast)
        response_objects.append(TellWeatherForecast(weather_forecast=weather_forecast))
        context.save()
    elif context.safe_access('place') is None and context.safe_access('date') is None:
        response_objects.append(RefineRequest(text='Вы хотели бы узнать погоду? В какой день и в каком городе?'))
    elif context.safe_access('place') is None:
        response_objects.append(RefineRequest(text='В каком городе ищем погоду?'))
    else:  # context.safe_access('date') is None
        response_objects.append(RefineRequest(text='На какое число нужен прогноз?'))

    return response_objects


def process_request_objects(request_objects: List[RequestObject], context: Context) -> List[ResponseObject]:
    """
    Takes a list of request objects,
    reacts to each of them with process_request_object(...)
    and merges these lists together and returns it
    :param request_objects: the request objects to parse
    :param context: current context of the user
    :return: a list of response objects, generated in response to the given request objects
    """
    response_objects = []
    for request_object in request_objects:
        response_objects.extend(process_request_object(request_object, context))
    context.save()
    return response_objects
