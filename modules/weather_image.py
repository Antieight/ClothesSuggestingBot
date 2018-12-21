import sys; sys.path.insert(0, '..')

import requests as re
from bs4 import BeautifulSoup
import urllib
import json
from random import randint
from constants.global_constants import *


def shortened_condition(condition):
    """Makes a keyword to be passed to the google query out of the full-form-condition

       Parameters:
           condition -- str -- the whole description of whether at some time

       Returns:
           keyword -- str -- somewhat shortened condition to be effectively
                              passed to google to get better pictures
    """
    if 'дожд' in condition.lower():
        return 'дождь'
    if condition.lower() in ['ясно', 'малооблачно', 'облачно с прояснениями']:
        return 'солнце'
    if 'солн' in condition.lower():
        return 'солнце'
    if 'снег' in condition.lower() or 'снеж' in condition.lower():
        return 'снежный'
    return 'тучи'


def get_image_path(city, condition):
    """Gets a link to a picture in the web, that represents both specified
       city and condition. Link choosing process contains randomness.

       Parameters:
           city -- str -- city name, better short for google to be effective
           condition -- str -- the whole description of what is going on
                               in the city specified at some time

       Returns:
           link -- str -- a link to an image, that shows the city in the condition"""
    condition = shortened_condition(condition)
    city = city.split(',')[0]

    def get_soup(url_: str, header_: dict):
        return BeautifulSoup(re.get(url_, headers=header_).text, 'html.parser')

    query = city + '+' + condition
    # image_type="Action"
    url = "https://www.google.co.in/search?q=" + query + "&source=lnms&tbm=isch"  # &tbs=isz:m"

    user_agent_ = '''
        Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36
    '''.strip()
    header = {'User-Agent': user_agent_}
    soup = get_soup(url, header)

    links = []
    for a in soup.find_all("div", {"class": "rg_meta"}):
        if (str(json.loads(a.text)["ou"]).endswith('jpg') or
            str(json.loads(a.text)["ou"]).endswith('png')) and (
                True):  # '%' not in str(json.loads(a.text)["ou"])):
            links.append(json.loads(a.text)["ou"])
    a = randint(0, min(4, len(links)))
    link = links[a]

    image_path: str = f"{ROOT_PATH}/data/images/{city}_{condition}." + link.split('.')[-1]
    urllib.request.urlretrieve(link, image_path)
    return image_path
