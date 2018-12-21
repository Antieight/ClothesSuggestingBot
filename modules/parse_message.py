import os, sys; sys.path.insert(0, '..')

from objects.context import Context
from objects.request_objects import RequestObject, Nonsense, CancelRequest
from modules.messages_classifier import classify_message
from modules.stories import feedback_story, wardrobe_story, clothes_story, weather_forecast_story, subscription_story
from constants.stories_constants import *
from modules.russian_language import *
from typing import Optional, List

"""
    This module is intended to parse the message. 
    It controls all the actions from the beginning to the end (of the parsing process).
"""

STORIES_MODULES = {
    STORY_WEATHER_FORECAST_REQUEST: weather_forecast_story,
    STORY_SUBSCRIPTION_MANAGEMENT: subscription_story,
    STORY_WARDROBE_MANAGEMENT: wardrobe_story,
    STORY_CLOTHES_SET_REQUEST: clothes_story,
    STORY_FEEDBACK: feedback_story
}


def refine_story(message: str, context: Context) -> Context:
    """
    Refines the context, that is classifies the message if its story is empty and saves it to disk
    :param message: the message, sent by the user
    :param context: the user's current context
    :return: refreshed context
    """
    if not context.has_story():
        story_id = classify_message(message)
        context.set_story(story_id=story_id)
        context.touch()
        context.set_info()
        context.save()
    return context


def parse_message(message: str, user_id: str) -> List[RequestObject]:
    """ The whole process of getting a request object by a text-message (str) """
    try:
        context = Context(user_id)
        if context.is_obsolete():
            context.set_story(STORY_NO_STORY)
            context.save()

        if take_away_punctuation(message).lower().split()[0] in ['отмена', 'отменить', 'выход', 'стоп']:
            if len(message) <= 10:
                return [CancelRequest()]

        refine_story(message, context)

        request_objects: List[RequestObject] = STORIES_MODULES[context.get_story()].parse_message(message=message,
                                                                                                  context=context)
        # first fallback:
        if request_objects is None or len(request_objects) == 0:
            context.set_story(story_id=STORY_NO_STORY)
            refine_story(message, context)
            request_objects: List[RequestObject] = STORIES_MODULES[context.get_story()].parse_message(message=message,
                                                                                                      context=context)
        # second fallback:
        if request_objects is None or len(request_objects) == 0:
            context.reset()
            request_objects = [Nonsense()]

        context.save()

        return request_objects

    except Exception:
        return [Nonsense()]
