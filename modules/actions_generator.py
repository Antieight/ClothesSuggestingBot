import sys; sys.path.insert(0, '..')

from random import choice
from objects.response_objects import *
from objects.action import Action, PrintAction, ShowImage, ShowPoll
from objects.weather_forecast import *
from objects.clothes import *
from constants.daytime_constants import *
from typing import List, Iterable, Type
from modules.weather_image import *


def choose_template(templates: List[str]) -> str:
    """ returns a random element of the given list (template choosing) """
    return choice(templates)


def generate_actions(response_objects: List[ResponseObject]) -> List[Action]:
    """
        This function accepts a list (or any other iterable) of response objects and converts them to Actions,
        that will be played by performer. Returns a list of Actions (see objects.action)
    """
    actions = []
    for response_object in response_objects:
        assert isinstance(response_object, ResponseObject)

        if isinstance(response_object, CommonApprove):
            templates = ['Хорошо!', 'Ок.', 'Отлично']
            actions.append(PrintAction(choose_template(templates)))

        elif isinstance(response_object, CommonMessage):
            actions.append(PrintAction(response_object.text))

        elif isinstance(response_object, ErrorUnableToParseMessage):
            template = 'У меня не получилось понять предыдущее сообщение. :(' # \n\n Подробности:\n{}'
            actions.append(PrintAction(template))

        elif isinstance(response_object, ErrorUnableToProcessRequest):
            actions.append(PrintAction('Мне не удалось выполнить действие, которое я понял.'))
            actions.append(PrintAction(response_object.request_object_understood.__class__.__name__))

        elif isinstance(response_object, TellWeatherForecast):
            weather_forecast = response_object.weather_forecast
            htmls = get_htmls_for_weather_forecast(weather_forecast)
            for html in htmls:
                actions.append(PrintAction(html))
            # we need to show some image as well
            try:
                day_forecast: DayForecast = list(weather_forecast)[0]
                forecast_frame: ForecastFrame = day_forecast[1]  # choosing day daytime_id
                image_path = \
                    get_image_path(weather_forecast.place, forecast_frame.common_state)
                actions.append(ShowImage(image_path, caption=weather_forecast.place))
            except Exception:
                actions.append(PrintAction('А картинку покажу в другой раз :)'))

        elif isinstance(response_object, ClothesSuggestion):
            clothes_set = response_object.clothes_set
            html = get_html_for_clothes_set(clothes_set)
            actions.append(PrintAction(html))

        elif isinstance(response_object, WardrobeShowResponse):
            wardrobe: Wardrobe = response_object.wardrobe
            html = get_html_for_wardrobe(wardrobe)
            actions.append(PrintAction(html))

        elif isinstance(response_object, ReclamationReply):
            clothes_set = response_object.clothes_set
            html = 'А как вам такой набор?\n' + get_html_for_clothes_set(clothes_set)
            html += '(Оценка  {})'.format(response_object.feedback)
            actions.append(PrintAction(html))

        elif isinstance(response_object, ShowSubscriptionsResponse):
            subscriptions: Subscriptions = response_object.subscriptions
            from constants.services_constants import SERVICE_CLOTHES_SET, SERVICE_WEATHER
            from modules.russian_language import set_case
            html = ''
            if subscriptions[SERVICE_WEATHER] is not None:
                html += 'Подписка на погоду в {}\n'.format(set_case(subscriptions[SERVICE_WEATHER]['place'], 'loct'))
            if subscriptions[SERVICE_CLOTHES_SET] is not None:
                html += 'Подписка на одежду в {}'.format(set_case(subscriptions[SERVICE_CLOTHES_SET]['place'], 'loct'))
            if html == '':
                html += 'Вы ни на что не подписаны.'
            actions.append(PrintAction(html))

        elif isinstance(response_object, SuccessfulSubscription):
            actions.append(PrintAction('Подписка про {} была успешно оформлена!'.format(response_object.text)))

        elif isinstance(response_object, SuccessfulUnsubscription):
            actions.append(PrintAction('Подписка про {} была удалена!'.format(response_object.text)))

        elif isinstance(response_object, WardrobeItemIdAdded):
            clothing_item_id = response_object.clothing_item_id
            clothing_item_name = get_clothing_item_name(clothing_item_id=clothing_item_id)
            actions.append(PrintAction('Вещь {} была успешно добавлена в гардероб!'.format(clothing_item_name)))

        elif isinstance(response_object, WardrobeItemIdAdded):
            clothing_item_id = response_object.clothing_item_id
            clothing_item_name = get_clothing_item_name(clothing_item_id=clothing_item_id)
            actions.append(PrintAction('Вещь {} была успешно удалена из гардероба!'.format(clothing_item_name)))

        elif isinstance(response_object, RefineRequest):
            actions.append(PrintAction(response_object.text))

        elif isinstance(response_object, FeedbackRequest):
            place = response_object.place
            date = response_object.date
            daytime_id = response_object.daytime_id
            daytime_name = DAYTIME_NAMES[daytime_id]
            months = '- января февраля марта апреля мая июня июля августа сентября октября ноября декабря'.split()
            html = 'Кажется, вы собирались погулять {0}го {1} ({3}) в {2}. Как ощущения?'
            html = html.format(date.day, months[date.month], place, daytime_name)
            actions.append(PrintAction(html))
        else:
            assert False, "Unknown response object"
    return actions
