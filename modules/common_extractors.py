import os, sys; sys.path.insert(0, '..')
import datetime
from functools import lru_cache

from modules.russian_language import *
from constants.global_constants import *
from constants.daytime_constants import *
from constants.feedback_constants import *
from constants.services_constants import *
from objects.clothes import *
from typing import Callable, List, Any, Optional, Tuple

"""
This file contains the most common extractors,
that takes a message (str) and try to extract some
specific kind of information.
"""

PatternFunctionType = Callable[[str], Any]


def pattern(func: PatternFunctionType) -> PatternFunctionType:
    """ pattern decorator, which makes a throwing function return None, instead of raising an Exception """
    def improved_func(sub_message: str) -> Any:
        try:
            return func(sub_message)
        except Exception:
            return None
    return improved_func


def apply_pattern(string: str, pattern_function: PatternFunctionType) -> List[Any]:
    """
    Applies the pattern_function to the string, that is tries to attach the pattern to each suffix of a string.
    :param string: a string to search the pattern in
    :param pattern_function: a pattern function, that gets applied to the string
    :return: a list of matches
    """
    words = string.split()
    results = []
    for i in range(len(words)):
        suffix = ' '.join(words[i:])
        # print('LOG: trying pattern {0} on suffix {1}'.format(pattern, suffix))

        result = pattern_function(suffix)
        if result is not None:
            results.append(result)
    return results


def apply_patterns(string: str, pattern_functions: List[PatternFunctionType]) -> List[Any]:
    """
    Tries several pattern_functions for the string.
    :param string: the string
    :param pattern_functions: a list of pattern-functions
    :return: a list of matches
    """
    results = []
    for pattern_function in pattern_functions:
        results += apply_pattern(string=string, pattern_function=pattern_function)
    return results


def rezip(list_of_tuples):
    """ swaps elements of each tuple in the list """
    return list(zip(*(list(zip(*list_of_tuples)))[::-1]))


@lru_cache(maxsize=512)
def extract_date(message: str) -> Optional[datetime.date]:
    today = (datetime.datetime.utcnow() + datetime.timedelta(3/24)).date()
    message = normalize_string(take_away_punctuation(message))
    # now each pattern operates on a suffix

    def convert_to_date(number: int) -> datetime.date:
        assert isinstance(number, int)
        return today + datetime.timedelta(number)

    @pattern
    def pattern_relative_specification_one_word(sub_message: str) -> datetime.date:
        words = sub_message.split()
        options = {'сегодня': 0, 'завтра': 1, 'послезавтра': 2, 'послепослезавтра': 3, 'сейчас': 0}
        return convert_to_date(options[words[0]])

    @pattern
    def pattern_relative_specification_with_after_week(sub_message: str) -> datetime.date:
        words = sub_message.split()
        n_days = None
        if words[0] == 'через':
            options = {'1': 7, 'один': 7}
            assert words[2] == 'неделя'
            n_days = options[words[1]]
        return convert_to_date(n_days)

    @pattern
    def pattern_relative_specification_with_after_day(sub_message: str) -> datetime.date:
        words = sub_message.split()
        n_days = None
        if words[0] == 'через':
            options = {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '0': 0,
                       'один': 1, 'два': 2, 'пара': 2, 'три': 3, 'тройка': 3, 'четыре': 4, 'пять': 5,
                       'шесть': 6, 'семь': 7, 'восемь': 8, 'девять': 9, 'ноль': 0}
            assert words[2] == 'день'
            n_days = options[words[1]]
        return convert_to_date(n_days)

    @pattern
    def pattern_relative_specification_with_after(sub_message: str) -> datetime.date:
        words = sub_message.split()
        n_days = None
        if words[0] == 'через':
            options = {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '0': 0,
                       'один': 1, 'два': 2, 'пара': 2, 'три': 3, 'тройка': 3, 'четыре': 4, 'пять': 5,
                       'шесть': 6, 'семь': 7, 'восемь': 8, 'девять': 9, 'ноль': 0, 'неделя': 7, 'день': 1}
            n_days = options[words[1]]
        return convert_to_date(n_days)

    @pattern
    def pattern_weekday(sub_message: str) -> datetime.date:
        words = sub_message.split()
        if words[0] in ['в', 'во']:
            words = words[1:]

        options = rezip(enumerate('понедельник вторник среда четверг пятница суббота воскресенье'.split(), start=1))
        options2 = rezip(enumerate('пн вт ср чт пт сб вс'.split(), start=1))
        options = dict((*options, *options2))
        target = options[get_normal_form(word=words[0])]
        today_weekday = today.isoweekday()
        return convert_to_date((target - today_weekday) % 7)

    @pattern
    def pattern_exact_date(sub_message):
        words = sub_message.split()
        if words[0].endswith('го'):
            words[0] = words[0][:-2]

        numbers = 'один два три четыре пять шесть семь восемь девять'
        numbers2 = '1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31'
        months = 'январь февраль март апрель май июнь июль август сентябрь октябрь ноябрь декабрь'
        opt1 = dict(rezip(enumerate(numbers.split(), start=1)))
        opt2 = dict(rezip(enumerate(numbers2.split(), start=1)))
        days = {**opt1, **opt2}
        day = days[get_normal_form(words[0])]
        months = dict(rezip(enumerate(months.split(), start=1)))
        months['числа'] = today.month
        month = months[get_normal_form(words[1])]
        year = today.year
        return datetime.date(day=day, month=month, year=year)

    patterns = [pattern_relative_specification_one_word, pattern_relative_specification_with_after,
                pattern_weekday, pattern_exact_date]

    matches = apply_patterns(message, patterns)
    if len(matches) > 0:
        return matches[0]
    return None


@lru_cache(maxsize=512)
def extract_place(message: str):
    normalize_string(take_away_punctuation(message))

    def extract_maybe_city(sub_message: str) -> str:
        """ 
            returns the quoted thing, if the sub_message starts with '"'
            otherwise simply returns the first word
        """
        if sub_message.startswith('"'):
            maybe_city = sub_message.split('"')[1]
        else:
            maybe_city = sub_message.split()[0]
        return maybe_city

    @pattern
    def pattern_exact_specification(sub_message: str) -> str:
        words = sub_message.split()
        assert get_normal_form(words[0]) == 'в'
        assert get_normal_form(words[1]) in ['город', 'поселок', 'село', 'деревня', 'мегаполис']
        rest = ' '.join(words[2:])
        maybe_city = extract_maybe_city(rest)
        return maybe_city

    @pattern
    def pattern_one_of_known_cities(sub_message: str) -> str:
        maybe_city = extract_maybe_city(sub_message).lower()
        path = os.path.join(ROOT_PATH, 'data', 'known_cities.txt')
        with open(path, 'r', encoding='utf8') as f:
            known_cities = f.readlines()
            for i, city in enumerate(known_cities):
                if city[-1] == '\n':
                    known_cities[i] = city[:-1]
                known_cities[i] = known_cities[i].lower()
        if maybe_city in known_cities:
            return maybe_city
        if normalize_string(maybe_city) in known_cities:
            return normalize_string(maybe_city)

    @pattern
    def pattern_return_exclude_weekdays(sub_message: str) -> str:
        words = sub_message.split()
        assert get_normal_form(words[0]) == 'в'
        rest = ' '.join(words[1:])
        weekdays = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс',
                    'понедельник', 'вторник', 'среда', 'четверг', 
                    'пятница', 'суббота', 'воскресенье']
        maybe_city = normalize_string(extract_maybe_city(rest))
        if maybe_city not in weekdays:
            return maybe_city

    patterns = [pattern_one_of_known_cities, pattern_exact_specification,
                pattern_return_exclude_weekdays]

    matches = apply_patterns(message, patterns)
    if len(matches) > 0:
        return matches[0]
    return None


@lru_cache(maxsize=512)
def extract_daytime_id(message: str) -> Optional[int]:
    """
    Extracts a daytime_id from a message
    :param message: message from which a daytime_id is being extracted
    :return: daytime_id - index of a daytime, found in the message
    """
    normalized_message = normalize_string(message)
    for daytime_id in DAYTIME_IDS:
        if DAYTIME_NAMES[daytime_id] in normalized_message:
            return daytime_id
    for daytime_id, daytime_name in enumerate(('утром', 'днем', 'вечером', 'ночью')):
        if daytime_name in normalized_message:
            return daytime_id
    if 'днём' in normalized_message:
        return 1
    if 'сейчас' in normalized_message:
        return 0
    return None


@lru_cache(maxsize=512)
def extract_clothes_set(message: str) -> Optional[ClothesSet]:
    """
    Extracts a clothes set object from the message.
    :param message: a message from which a clothes set is being extracted
    :return: a ClothesSet object, that contains all the clothing items, that were found or None if none
    """
    clothes_dict = dict()
    words = message.split()

    def has_comma_after(words_position: int):
        if words_position > len(words):
            return True
        return words[words_position].endswith(PUNCTUATION)

    normalized_message = normalize_string(take_away_punctuation(message))
    normalized_message_words = normalized_message.split()
    message_words = take_away_punctuation(message).split()
    message_words_to_index = {b: a for a, b in enumerate(normalized_message_words)}
    message_words_to_index.update({b: a for a, b in enumerate(message_words)})
    all_message_words_set = set(message_words_to_index.keys())

    clothing_items_names = get_clothing_items_names()
    normalized_items_names = list(map(normalize_string, get_clothing_items_names()))
    clothing_item_name_to_index = {b: a for a, b in enumerate(clothing_items_names)}
    clothing_item_name_to_index.update({b: a for a, b in enumerate(normalized_items_names)})
    all_clothing_items_names_set = set(clothing_item_name_to_index.keys())

    clothes_objects_found = all_message_words_set & all_clothing_items_names_set
    locations = [message_words_to_index[clothing_object] for clothing_object in clothes_objects_found]
    clothing_items_names = [clothing_items_names[clothing_item_name_to_index[clothing_object]]
                            for clothing_object in clothes_objects_found]
    locations_and_cinames = sorted(list(set(zip(locations, clothing_items_names))), key=lambda x: x[0], reverse=True)

    # for each clothing item we look for wearing_degree keyword in some neighbourhood
    for index, clothing_item in locations_and_cinames:
        indices: tuple = tuple(index + i for i in [-1, 1]
                               if -1 < index + i < len(normalized_message_words) and
                               ((i == -1 and not has_comma_after(index - 1)) or
                               (i == 1 and not has_comma_after(index))))
        endings: tuple = ('ый', 'ий', 'ой', 'ые', 'ое', 'ие', 'ее', 'ая', 'яя')
        wearing_degree_specifications = {
            WEARING_DEGREE_AVERAGE: ('прост', 'обычн'),                 # простой, обычный
            WEARING_DEGREE_LIGHT: ('легк', 'лёгк', 'рван', 'тонк'),     # легкий, рваный, тонкий
            WEARING_DEGREE_COOL: ('прохладн', 'холодн'),                # прохладный, холодный
            WEARING_DEGREE_SOLID: ('плотн', ),                          # плотное
            WEARING_DEGREE_WARM: ('тепл', 'тёпл'),                      # теплая
            WEARING_DEGREE_HOT: ('ультратёпл', 'горяч',
                                 'шерстян', 'пухов', 'ультратепл')      # горячее, ультратеплое, шерстяное, пуховое
        }
        wearing_degree_specifications = {val: key
                                         for key, values in wearing_degree_specifications.items()
                                         for val in values}
        specification = WEARING_DEGREE_AVERAGE
        for ind in indices:
            maybe_spec = normalized_message_words[ind]
            if maybe_spec[-2:] in endings and maybe_spec[:-2] in wearing_degree_specifications:
                specification = wearing_degree_specifications[maybe_spec[:-2]]
                normalized_message_words[ind] += '_used'
        clothes_dict[clothing_item] = specification

    if len(clothes_dict) == 0:
        return None

    clothes_set = ClothesSet()
    for clothing_item, wearing_degree_id in clothes_dict.items():
        clothes_set.wear(clothing_item=clothing_item, wearing_degree_id=wearing_degree_id)
    return clothes_set if not clothes_set.is_empty() else None


@lru_cache(maxsize=512)
def extract_feedback(message: str) -> Optional[FeedbackType]:
    """
    Extracts a single feedback out of message
    :param message: a message from which a feedback is being extracted
    :return: a number from FEEDBACK_RANGE
    """
    words: Tuple[str] = tuple(take_away_punctuation(normalize_string(message)).split())
    pre_words_prefixes = {
        'очень': 1, 'ужасно': 2, 'не': -2, 'невыносим': 0
    }
    keywords_prefixes = {
        'холод': -3, 'мороз': -3, 'прохлад': -2, 'зябк': -2, 'неприятн': -1, 'нормаль': 0, 'ок': 0, 'хорош': 0,
        'отличн': 0, 'замечат': 0, 'превосход': 0, 'прекрасн': 0, 'тепл': 0, 'вспоте': 2, 'жар': 3, 'горяч': 3,
        'зажар': 3, 'запар': 3
    }

    def is_pre_word(pre_word: str) -> Optional[str]:
        """ Returns a prefix for the pre_word if it is indeed a pre_word, otherwise None """
        for pre_word_prefix in pre_words_prefixes:
            if pre_word.startswith(pre_word_prefix):
                return pre_word_prefix

    def is_keyword(keyword: str) -> Optional[str]:
        """ Returns a prefix for the keyword if it is indeed a keyword, otherwise None """
        for keyword_prefix in keywords_prefixes:
            if keyword.startswith(keyword_prefix):
                return keyword

    pre_word_affect = 0
    pre_word_dist = -1
    for word in words:
        if pre_word_dist >= 0:
            pre_word_dist += 1
        if pre_word_dist == 2:
            pre_word_affect = 0
            pre_word_dist = 0
        pre_word_prefix = is_pre_word(word)
        keyword_prefix = is_keyword(word)
        if pre_word_prefix:
            pre_word_affect = pre_words_prefixes[word]
            pre_word_dist = 0
        elif keyword_prefix:
            effect = keywords_prefixes[keyword_prefix] + pre_word_affect
            return effect

    feedbacks = ('-5', '-4', '-3', '-2', '-1', '0', '1', '2', '3', '4', '5')
    for word in words:
        if word in feedbacks:
            return int(word)
    return None


@lru_cache(maxsize=512)
def extract_zones_feedback(message: str) -> Optional[ZoneFeedbackType]:
    """
    Extracts zones_feedback array out of the message.
    :param message: a message from which a zones_feedback array is being extracted from
    :return: zones_feedback if such was found
    """
    zones_feedback = [0] * len(ZONES)
    normed_words = normalize_string(take_away_punctuation(message)).split()
    words = message.split()

    def has_break_after(index: int) -> bool:
        """ Returns whether there is a break after the word at position index in the original message"""
        return words[index].endswith((',', '.', ';', '!', '?'))

    normalized_zones_names_ru = list(map(normalize_string, ZONES_NAMES_RU))
    for zone_id, zone_name in enumerate(normalized_zones_names_ru):
        related_feedback = 0
        if normed_words.count(zone_name):
            index = normed_words.index(zone_name)
            from_position = index
            to_position = index
            for _ in range(3):
                if from_position != 0 and not has_break_after(from_position - 1):
                    from_position -= 1
                if to_position != len(words) - 1 and not has_break_after(to_position):
                    to_position += 1
            related_feedback = extract_feedback(message[from_position: to_position + 1])
        zones_feedback[zone_id] = related_feedback

    return zones_feedback if (set(zones_feedback)) != {0} else None


@lru_cache(maxsize=512)
def extract_subscription_service_id(message: str) -> Optional[int]:
    """
    Extracts the subscription type if any is present
    :param message: a message from which the subscription type is being extracted
    :return: the contained subscription type id if such is present
    """
    normed_words = normalize_string(take_away_punctuation(message)).split()
    weather_subscription_indicators = {'прогноз', 'погода'}
    clothes_subscription_indicators = {'надевать', 'одевать', 'одеваться', 'вещь', 'одежда'}
    if len(set(normed_words) & weather_subscription_indicators) > 0:
        return SERVICE_WEATHER
    elif len(set(normed_words) & clothes_subscription_indicators) > 0:
        return SERVICE_CLOTHES_SET
    else:
        return None


@lru_cache(maxsize=512)
def extract_subscription_period(message: str) -> Optional[int]:
    """
    Extracts, how often a user wants our messages to be delivered to him
    :param message: a message from which the period is being extracted
    :return: a subscription period if such is present
    """
    normalized_message = normalize_string(take_away_punctuation(message))

    @pattern
    def pattern_main(sub_message: str) -> Optional[int]:
        words = sub_message.split()
        numbers = {b: a for a, b in enumerate('0123456789')}
        numbers.update({b: a for a, b in enumerate(('ноль', 'один', 'два', 'три', 'четыре', 'пять',
                                                    'шесть', 'семь', 'восемь', 'девять', 'десять', 'одиннадцать',
                                                    'двенадцать', 'тринадцать', 'четырнадцать'))})
        if words[0] in numbers and words[1] == 'раз' and words[2] in ['в', 'во', 'на']:
            if words[3] == 'день':
                return 1 // numbers[words[0]]
            elif words[3] == 'неделя':
                return 7 // numbers[words[0]]
            elif words[3] == 'месяц':
                return 30 // numbers[words[0]]
            elif words[3] == 'год':
                return 365 // numbers[words[0]]
        else:
            return None

    @pattern
    def pattern_simple(sub_message: str) -> Optional[int]:
        # раз в день/неделю/месяц
        words = sub_message.split()
        if words[0] == 'раз' and words[2] in ['в', 'во', 'на']:
            return pattern_main(' '.join(['1', *words]))
        return None

    @pattern
    def yet_another_pattern(sub_message: str) -> Optional[int]:
        words = sub_message.split()
        numbers = {b: a for a, b in enumerate('0123456789')}
        numbers.update({b: a for a, b in enumerate(('ноль', 'один', 'два', 'три', 'четыре', 'пять',
                                                    'шесть', 'семь', 'восемь', 'девять', 'десять', 'одиннадцать',
                                                    'двенадцать', 'тринадцать', 'четырнадцать'))})
        num = numbers[words[2]]
        assert words[0] == 'раз'
        assert words[1] in ['в', 'во']
        assert words[3] in ['день', 'неделя']
        return num if words[3] == 'день' else num // 7

    patterns = [pattern_main, pattern_simple, yet_another_pattern]

    matches = apply_patterns(normalized_message, patterns)
    if len(matches) > 0:
        return matches[0]
    return None


@lru_cache(maxsize=512)
def extract_subscription_operation_type(message: str) -> Optional[int]:
    """
    Extracts, whether a user wants to subscribe or unsubscribe
    :param message: a message, that's being analyzed
    :return: -1 if unsubscribe, 1 is subscribe
    """
    unsubscribe_indicators = {'не', 'остановись', 'прекратить', 'закончить', 'закончи', 'прекрати', 'больше',
                              'хватит', 'отписать', 'отписаться', 'отпиши', 'отменить', 'отмени'}
    subscribe_indicators = {'подписаться', 'подписка', 'подписываться', 'добавить', 'присылай', 'добавь'}
    normalized_words = normalize_string(take_away_punctuation(message)).split()
    words = message.split()
    if len({*words, *normalized_words} & unsubscribe_indicators) > 0:
        return -1
    elif len({*words, *normalized_words} & subscribe_indicators) > 0:
        return 1
    else:
        return None


@lru_cache(maxsize=512)
def extract_clothing_item_id(message: str) -> Optional[int]:
    """
    Extracts clothing item from the message passed
    :param message: a message from which the clothing_item_id is being extracted
    :return: a clothing item id if such is found
    """
    normalized_message = normalize_string(take_away_punctuation(message))
    words = set(normalized_message)
    clothing_items_names = set(get_clothing_items_names())
    common = words & clothing_items_names
    if len(common) > 0:
        return list(common)[0]
    return None


@lru_cache(maxsize=512)
def extract_zone_id(message: str) -> Optional[int]:
    """
    Extract the zone_id if recognizes one
    :param message: a message that's being analyzed
    :return: an integer, that represents a zone_id
    """
    normalized_message_words = set(normalize_string(take_away_punctuation(message)).split())
    normalized_zones_names_ru = list(map(normalize_string, ZONES_NAMES_RU))
    common = set(normalized_zones_names_ru) & normalized_message_words
    if len(common) > 0:
        return normalized_zones_names_ru.index(list(common)[0])
    return None


@lru_cache(maxsize=512)
def extract_wardrobe_operation(message: str) -> Optional[int]:
    """
    Extracts a wardrobe operation type, if founds one
    :param message: a string from which the operation is extracted
    :return: -1 if remove from wardrobe, 1 if add, 0 if show
    """

    add_indicators = {'добавить', 'занести', 'купить', 'положить', 'присоединить', 'добавь', 'положи'}
    remove_indicators = {'убрать', 'выкинуть', 'удалить', 'вынести', 'выбросить',
                         'уничтожить', 'выкинь', 'убери', 'удали'}
    show_indicators = {'покажи', 'показать', 'гардеробе', 'открой', 'открыть', 'что'}
    normalized_words = set(normalize_string(take_away_punctuation(message)))
    united_words = {*normalized_words, *(message.split())}
    if len(add_indicators & united_words) > 0:
        return 1
    elif len(remove_indicators & united_words) > 0:
        return -1
    elif len(show_indicators & united_words) > 0:
        return 0
    else:
        return None


@lru_cache(maxsize=512)
def extract_approval(message: str) -> Optional[bool]:
    """
    Extracts, whether the user did approve something
    :param message: a message, that is being analyzed
    :return: True if the user agrees, None otherwise
    """
    approval_indicators = {'да', 'ок', 'ok', 'хорошо', 'конечно', 'ладно', 'норм', 'нормально', 'пойдет', 'спасибо',
                           'нормал', 'пойдёт', 'норма'}
    normalized_words = set(normalize_string(take_away_punctuation(message)).split())
    words = set(take_away_punctuation(message).split())
    if len(approval_indicators & (words | normalized_words)) > 0:
        return True
    return None

