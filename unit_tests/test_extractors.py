import os, sys; sys.path.insert(0, '..')

import datetime
from modules.common_extractors import *
from typing import Tuple


def test_extractors():
    messages = (
        'Погода сегодня в Париже',
        'Какая погода в москве через 4 дня',
        'Что с погодой завтра в Суздале',
        'Погода в Минске в пятницу',
        'В Берлине через неделю'
    )
    today: datetime.date = (datetime.datetime.utcnow() + datetime.timedelta(3/24)).date()

    def convert_to_date(number: int) -> datetime.date:
        assert isinstance(number, int)
        return today + datetime.timedelta(number)

    dates: Tuple[datetime.date] = (today, convert_to_date(4), convert_to_date(1),
                                   convert_to_date((5 - today.isoweekday()) % 7),
                                   convert_to_date(7))

    places: Tuple[str] = ['париж', 'москва', 'суздаль', 'минск', 'берлин']

    for message, correct_date, correct_place in zip(messages, dates, places):
        date = extract_date(message)
        place = extract_place(message)
        # print(message, '\t:\t', date, place)
        assert date == correct_date, 'date: ' + message
        assert place == correct_place, 'place: ' + message
