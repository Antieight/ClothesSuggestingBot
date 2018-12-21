import sys; sys.path.insert(0, '..')

from constants.stories_constants import *
from modules.russian_language import *
from objects.clothes import get_clothing_items_names

"""
    This module attempts to classify the message in situation, when the context is empty or obsolete
"""


def classify_message(message: str) -> int:
    """ Takes a message and tries to guess the story without any other knowledge. Returns the story_id """
    normalized_message = take_away_punctuation(normalize_string(message))
    associated_words = {
        STORY_WEATHER_FORECAST_REQUEST: {'погода', 'какая', 'что', 'прогноз'},
        STORY_SUBSCRIPTION_MANAGEMENT: {'подписка', 'подписаться', 'рассылка', 'присылать',
                                        'ежедневно', 'каждый', 'рассказывать', 'подпиши', 'отпиши', 'отписка',
                                        'перестань'},
        STORY_WARDROBE_MANAGEMENT: {'гардероб', 'добавить', 'удалить', *get_clothing_items_names(),
                                    'купить', 'потерять', 'порваться'},
        STORY_CLOTHES_SET_REQUEST: {'что', 'надеть', 'одеть', 'одеться', 'облачиться', 'напялить', 'бы',
                                    'одежда', 'одежду', 'сгенерировать', 'сгенерируем'},
        STORY_FEEDBACK: {'тепло', 'холодно', 'холодный', 'замерзнуть', 'зажариться', 'вспотеть',
                         'продуть', 'было', 'хотеть', 'хорошо',
                         *[str(i) for i in range(-5, 6)]}
    }
    multipliers = {
        STORY_WEATHER_FORECAST_REQUEST: 1,
        STORY_SUBSCRIPTION_MANAGEMENT: 10,
        STORY_WARDROBE_MANAGEMENT: 10,
        STORY_CLOTHES_SET_REQUEST: 1,
        STORY_FEEDBACK: 1
    }
    words = {*message.split(), *normalized_message.split()}
    scores = {
        STORY_WEATHER_FORECAST_REQUEST: 0.5,
        STORY_SUBSCRIPTION_MANAGEMENT: 0,
        STORY_WARDROBE_MANAGEMENT: 0,
        STORY_CLOTHES_SET_REQUEST: 0,
        STORY_FEEDBACK: 0
    }
    for story in associated_words:
        scores[story] += len(associated_words[story] & words)
        scores[story] *= multipliers[story]
    max_score = max(scores.values())
    for story in scores:
        if scores[story] == max_score:
            return story
