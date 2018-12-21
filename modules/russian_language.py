import sys; sys.path.insert(0, '..')
import pymorphy2
from typing import Optional

morph = pymorphy2.MorphAnalyzer()


def get_normal_form(word: str) -> str:
    """ Returns the normal form of the given word """
    assert isinstance(word, str)
    assert ' ' not in word
    return morph.parse(word)[0].normal_form


def normalize_string(string: str) -> str:
    """ Normalizes each word in a string and returns it """
    return ' '.join(list(map(get_normal_form, string.lower().split())))


PUNCTUATION = tuple(',.?!:;()[]{}')


def take_away_punctuation(string: str) -> str:
    """ Takes away punctuation chars from the string """
    for char in PUNCTUATION:
        string = string.replace(char, '')
    return string


def set_case(word: str, case: str) -> str:
    """ Returns the needed case (e.g. nominative, genetive, dative, accusative, ablative, prepositional """
    try:
        return morph.parse(word)[0].inflect({case}).word
    except Exception:
        return word


def get_number(word: str) -> str:
    """ Returns number (sing / plur) """
    try:
        if word == 'джинсы':
            return 'plur'
        return morph.parse(word)[0].tag.number
    except Exception:
        return 'sing'


def get_gender(word: str) -> Optional[str]:
    """ Returns the gender of the passed word"""
    try:
        if word == 'джинсы':
            return None
        return morph.parse(word)[0].tag.gender
    except Exception:
        return 'masc'


def set_word(word: str, case: str = 'nomn', number: str = 'sing', gender: str = 'masc') -> str:
    """ Returns the word with needed properties """
    try:
        if gender is None:
            return morph.parse(word)[0].inflect({case, number}).word
        else:
            return morph.parse(word)[0].inflect({case, number, gender}).word
    except Exception:
        return word
