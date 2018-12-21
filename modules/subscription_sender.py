import os, sys; sys.path.insert(0, '..')
from constants.global_constants import *
from typing import List
from objects.subscription import Subscriptions
from constants.services_constants import is_valid_service_id, SERVICE_WEATHER, SERVICE_CLOTHES_SET
from modules.processing_module import process_request_objects
from modules.actions_generator import generate_actions
from modules.performer import do_actions
from objects.request_objects import WeatherRequest, ClothesSetRequest
from constants.daytime_constants import *
import datetime


def send_subscriptions(bot) -> None:
    """
    Sends out all the subscriptions
    :return: None
    """
    user_ids: List[str] = os.listdir(USERS_PATH)
    for user_id in user_ids:
        user_path = os.path.join(USERS_PATH, user_id)
        user_chat_id_path = os.path.join(user_path, 'chat_id.txt')

        subscriptions = Subscriptions(user_id=user_id)
        request_objects = []
        today = datetime.date.today()

        if subscriptions[SERVICE_WEATHER] is not None:
            request_object = WeatherRequest(place=subscriptions[SERVICE_WEATHER]['place'],
                                            date=today)
            request_objects.append(request_object)
        if subscriptions[SERVICE_CLOTHES_SET] is not None:
            ClothesSetRequest(date=today, place=subscriptions[SERVICE_CLOTHES_SET]['place'],
                              daytime_id=DAYTIME_EVENING)
            pass

        if len(request_objects) == 0:
            print('no requests for user {}'.format(user_id))
            continue
        else:
            print(request_objects[0], request_objects[0].__dict__)
        with open(user_chat_id_path, 'r') as f:
            chat_id = f.readline()

        response_objects = process_request_objects(request_objects, user_id)
        print(response_objects, len(response_objects))
        actions = generate_actions(response_objects)
        do_actions(actions=actions, bot=bot, chat_id=chat_id)
