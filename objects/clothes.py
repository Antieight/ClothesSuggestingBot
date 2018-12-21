import sys; sys.path.insert(0, '..')
import os

from json import dumps, loads
from objects.serialization import Serializable
from typing import Union, List
from modules.russian_language import *
from constants.global_constants import USERS_PATH


# Hand  items will get ids from      [4000-4999]
# Head  items will get ids from      [3000-3999]
# Torso items will get ids from      [2000-2999]
# Legs  items will get ids from      [1000-1999]
# Foot  items will get ids from      [0000-0999]

ZONES_NAMES = ['FEET', 'LEGS', 'TORSOS', 'HEADS', 'HANDS']
ZONES_NAMES_RU = ['ступни', 'ноги', 'тело', 'голова', 'руки']
HEADS = ['HAT', 'CAP', 'PANAMA', 'USHANKA', 'BONNET', 'HEADSCARF', 'HOOD']
HEADS_RU = ['шапка', 'кепка', 'панама', 'ушанка', 'шляпа', 'платок', 'капюшон']
TORSOS = ['TSHIRT', 'SWEATER', 'SWEATSHIRT', 'TURTLENECK', 'UNDERSHIRT', 'JACKET', 'COAT', 'DOWNJACKET', 'CARDIGAN',
          'OVERCOAT', 'SHIRT']
TORSOS_RU = ['футболка', 'свитер', 'толстовка', 'водолазка', 'майка', 'пиджак', 'куртка', 'пуховик', 'кофта', 'пальто',
             'рубашка']
LEGS = ['TROUSERS', 'PANTS', 'JEANS', 'SHORTS', 'DRAWERS', 'TIGHTS']
LEGS_RU = ['брюки', 'штаны', 'джинсы', 'шорты', 'подштанники', 'колготки']
FEET = ['SNEAKERS', 'KEDS', 'SHOUES', 'BOOTS', 'WELLINGTONS', 'SANDALS', 'SOCKS']
FEET_RU = ['кроссовки', 'кеды', 'туфли', 'ботинки', 'сапоги', 'сандали', 'носки']
HANDS = ['GLOVES']
HANDS_RU = ['перчатки']
ZONES = [FEET, LEGS, TORSOS, HEADS, HANDS]                      # the order is important here
ZONES_RU = [FEET_RU, LEGS_RU, TORSOS_RU, HEADS_RU, HANDS_RU]    # the order is important here

assert len(ZONES_NAMES) == len(ZONES_NAMES_RU) == len(ZONES) == len(ZONES_RU)
for _zone_name in ZONES_NAMES:
    assert eval('len({0}) == len({0}_RU)'.format(_zone_name))

CLOTHING_ITEMS = dict()
for _zone_id, _zone in enumerate(ZONES_RU):
    for _clothing_item_id, _clothing_item_name in enumerate(_zone):
        CLOTHING_ITEMS[_zone_id * 1000 + _clothing_item_id] = _clothing_item_name


def get_clothing_items_ids() -> list:
    """ Returns the list of clothing items ids """
    return list(CLOTHING_ITEMS.keys())


def get_clothing_items_names() -> list:
    """ Returns the list of clothing items names """
    return list(CLOTHING_ITEMS.values())


def get_zones_names() -> list:
    """ Returns the list of russian names of zones """
    return ZONES_NAMES_RU


def get_clothing_item_id(clothing_item_name):
    zones_indicators = [zone.count(clothing_item_name) for zone in ZONES_RU]
    assert max(zones_indicators) > 0
    zone_id = [index for index, el in enumerate(zones_indicators) if el == max(zones_indicators)][0]
    index = ZONES_RU[zone_id].index(clothing_item_name)
    return 1000 * zone_id + index


def refine_clothing_item_id(clothing_item: Union[str, int]) -> int:
    """
        Takes a clothing item, which is either a clothing item id or a clothing item name
        Figures which it is
        Returns a clothing_item_id, that corresponds to that clothing item
    """
    if isinstance(clothing_item, str):
        # the clothing_item_name is passed
        clothing_item_id = get_clothing_item_id(clothing_item_name=clothing_item)
    elif isinstance(clothing_item, int):
        # the clothing_item_id is passed
        clothing_item_id = clothing_item
    else:
        assert False
    return clothing_item_id


def get_clothing_items_count(zone_id: int = None) -> int:
    """
        returns the number of clothing items for the specified zone_id,
        or the number of all the clothing items, if zone_id is None
    """
    assert isinstance(zone_id, (int, type(None)))
    return len(CLOTHING_ITEMS) if zone_id is None else len(ZONES[zone_id])


def get_zone_id(clothing_item_id: int) -> int:
    """  returns clothes_type by id. 0 means foot, 1 - leg, 2 - torso, 3 - head, 4 - hands"""
    assert isinstance(clothing_item_id, int)
    return clothing_item_id // 1000


def is_valid_zone_id(zone_id: int) -> bool:
    """ returns, whether zone_id is a valid zone id """
    assert isinstance(zone_id, int)
    return zone_id in range(len(ZONES))


def is_valid_clothing_item_id(clothing_item_id: int) -> bool:
    """ check whether given id is a valid one """
    assert isinstance(clothing_item_id, int)
    zone_id = get_zone_id(clothing_item_id)
    return is_valid_zone_id(zone_id) and clothing_item_id % 1000 < get_clothing_items_count(zone_id)


def get_clothing_item_name(clothing_item_id: int) -> str:
    """ returns russian name of the clothing item with provided id """
    assert is_valid_clothing_item_id(clothing_item_id), 'get_clothing_item_name: id is not valid: {}'.format(
        get_clothing_item_name)
    zone_id = get_zone_id(clothing_item_id)
    return ZONES_RU[zone_id][clothing_item_id % 1000]


def get_clothing_items_ids_by_zone(zone_id: int) -> List[int]:
    """
    Returns the ids of clothing items from the zone with a given id
    :param zone_id: zone id
    :return: list of clothing items
    """
    assert is_valid_zone_id(zone_id)
    zone = ZONES_RU[zone_id]
    return [get_clothing_item_id(clothing_item_name) for clothing_item_name in zone]


WEARING_DEGREES = ['NONE', 'COOL', 'LIGHT', 'AVERAGE', 'SOLID', 'WARM', 'HOT']
WEARING_DEGREES_RU = ['отсутствующий', 'холодный', 'легкий', 'средний', 'плотный', 'теплый', 'горячий']
assert len(WEARING_DEGREES) == len(WEARING_DEGREES_RU), 'missing translation for some wearing degree item'


def is_valid_wearing_degree_id(wearing_degree_id: int) -> bool:
    """ returns, whether id is a valid clothes degree identifier """
    assert isinstance(wearing_degree_id, int)
    return wearing_degree_id in range(len(WEARING_DEGREES))


def get_wearing_degree_name(wearing_degree_id: int) -> str:
    """ returns russian name for the clothes degree by id """
    assert is_valid_wearing_degree_id(wearing_degree_id)
    return WEARING_DEGREES_RU[wearing_degree_id]


def get_wearing_degree_id(wearing_degree_name: str) -> int:
    return WEARING_DEGREES.index(wearing_degree_name)


# setting clothes_degree constants
# for i, item in enumerate(WEARING_DEGREES):
#     exec('WEARING_DEGREE_' + item + ' = ' + str(i))
# I wanted autocomplete, so:
WEARING_DEGREE_NONE = get_wearing_degree_id('NONE')
WEARING_DEGREE_COOL = get_wearing_degree_id('COOL')
WEARING_DEGREE_LIGHT = get_wearing_degree_id('LIGHT')
WEARING_DEGREE_AVERAGE = get_wearing_degree_id('AVERAGE')
WEARING_DEGREE_SOLID = get_wearing_degree_id('SOLID')
WEARING_DEGREE_WARM = get_wearing_degree_id('WARM')
WEARING_DEGREE_HOT = get_wearing_degree_id('HOT')


class _Zone:
    """ Base class for all the zones, that represents one of ['ступни', 'ноги', 'торс', 'голова', 'руки'] """
    def __init__(self, zone_id: int) -> None:
        assert is_valid_zone_id(zone_id)
        self.clothes_set = [WEARING_DEGREE_NONE] * get_clothing_items_count(zone_id)
        self.zone_id = zone_id

    def wear(self, clothing_item: Union[int, str], wearing_degree_id: int = WEARING_DEGREE_AVERAGE):
        clothing_item_id = refine_clothing_item_id(clothing_item)
        assert is_valid_clothing_item_id(clothing_item_id)
        assert is_valid_wearing_degree_id(wearing_degree_id)
        self[clothing_item_id] = wearing_degree_id

    def take_off(self, clothing_item: Union[str, int]):
        self.wear(clothing_item, wearing_degree_id=WEARING_DEGREE_NONE)

    def __getitem__(self, clothing_item_id: int) -> int:
        assert get_zone_id(clothing_item_id) == self.zone_id
        return self.clothes_set[clothing_item_id % 1000]

    def __setitem__(self, clothing_item_id: int, wearing_degree_id: int) -> None:
        assert is_valid_clothing_item_id(clothing_item_id)
        assert get_zone_id(clothing_item_id) == self.zone_id
        self.clothes_set[clothing_item_id % 1000] = wearing_degree_id

    def __iter__(self):
        return iter([self.zone_id * 1000 + index
                     for index, wearing_degree in enumerate(self.clothes_set)
                     if wearing_degree != WEARING_DEGREE_NONE])

    def _to_string(self) -> str:
        return dumps([self.clothes_set, self.zone_id])

    def _from_string(self, string: str) -> None:
        assert isinstance(string, str)
        self.clothes_set, self.zone_id = loads(string)


class HeadsZone(_Zone):
    """ class that stores head clothing items. each clothing item has its degree of being weared from 0 up to 6 """

    def __init__(self):
        super(HeadsZone, self).__init__(ZONES.index(HEADS))


class TorsosZone(_Zone):
    """ class that stores torso clothing items. each clothing item has its degree of being weared from 0 up to 6 """

    def __init__(self):
        super(TorsosZone, self).__init__(ZONES.index(TORSOS))


class LegsZone(_Zone):
    """ class that stores legs clothing items. each clothing item has its degree of being weared from 0 up to 6 """

    def __init__(self):
        super(LegsZone, self).__init__(ZONES.index(LEGS))


class FeetZone(_Zone):
    """ class that stores feet clothing items. each clothing item has its degree of being weared from 0 up to 6 """

    def __init__(self):
        super(FeetZone, self).__init__(ZONES.index(FEET))


class HandsZone(_Zone):
    """ class that stores hands clothing items. each clothing item has its degree of being weared from 0 up to 6 """

    def __init__(self):
        super(HandsZone, self).__init__(ZONES.index(HANDS))


def is_zone_object(obj):
    return issubclass(obj, _Zone)


class ClothesSet:
    """
        Class that stores the clothes set, distributed between zones.
        You can pass the initial list of clothing items.
    """

    def __init__(self, clothing_items_list: Union[list, tuple, set] = None) -> None:
        """ clothing_items_list is a list of clothing_items_ids """
        self.heads = HeadsZone()
        self.torsos = TorsosZone()
        self.legs = LegsZone()
        self.feet = FeetZone()
        self.hands = HandsZone()
        self.zones = [self.feet, self.legs, self.torsos, self.heads, self.hands]
        if clothing_items_list is not None:
            for clothing_item in clothing_items_list:
                clothing_item_id = refine_clothing_item_id(clothing_item)
                self.wear(clothing_item_id)

    def wear(self, clothing_item: Union[str, int], wearing_degree_id : int = WEARING_DEGREE_AVERAGE) -> None:
        clothing_item_id = refine_clothing_item_id(clothing_item)
        assert is_valid_clothing_item_id(clothing_item_id)
        assert is_valid_wearing_degree_id(wearing_degree_id)
        self[clothing_item_id] = wearing_degree_id

    def take_off(self, clothing_item: Union[str, int]) -> None:
        self.wear(clothing_item, wearing_degree_id=WEARING_DEGREE_NONE)

    def to_string(self) -> str:
        return dumps([zone._to_string() for zone in self.zones])

    def from_string(self, string: str) -> None:
        assert isinstance(string, str)
        ClothesSet.__init__(self)
        for zone, dumped_zone in zip(self.zones, loads(string)):
            zone._from_string(dumped_zone)

    @staticmethod
    def create_from_string(string: str):
        assert isinstance(string, str)
        clothes_set = ClothesSet()
        clothes_set.from_string(string)
        return clothes_set

    def __getitem__(self, clothing_item: Union[int, str]) -> int:
        clothing_item_id = refine_clothing_item_id(clothing_item)
        assert is_valid_clothing_item_id(clothing_item_id)
        zone_id = get_zone_id(clothing_item_id)
        return self.zones[zone_id][clothing_item_id]

    def __setitem__(self, clothing_item: Union[int, str], wearing_degree_id: int) -> None:
        clothing_item_id = refine_clothing_item_id(clothing_item)
        assert is_valid_clothing_item_id(clothing_item_id)
        zone_id = get_zone_id(clothing_item_id)
        self.zones[zone_id][clothing_item_id] = wearing_degree_id

    def __iter__(self):
        return iter([el for zone in self.zones for el in list(zone)])

    def is_empty(self):
        return len(list(self)) == 0


class Wardrobe(ClothesSet, Serializable):
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        super(Wardrobe, self).__init__()
        self.load(user_id)

    def _first_time_init(self) -> None:
        super(Wardrobe, self).__init__()
        for clothing_item_id in get_clothing_items_ids():
            self.add_item(clothing_item_id)

    def _get_folder(self) -> str:
        return os.path.join(USERS_PATH, str(self.user_id))

    def _get_filename(self) -> str:
        return os.path.join(self._get_folder(), 'wardrobe.json')

    def has(self, clothing_item_id: int) -> bool:
        return self[clothing_item_id] != WEARING_DEGREE_NONE

    def doesnt_have(self, clothing_item_id: int) -> bool:
        return not self.has(clothing_item_id)

    def add_item(self, clothing_item: Union[int, str]) -> None:
        self.wear(clothing_item)

    def remove_item(self, clothing_item: Union[str, int]) -> None:
        self.take_off(clothing_item)

    def _pack(self) -> None:
        str_representation = self.to_string()
        user_id = self.user_id
        self.__dict__ = dict()
        self.user_id = user_id
        self.__dict__['str_representation'] = str_representation

    def _unpack(self) -> None:
        str_representation = self.str_representation
        self.__dict__.pop('str_representation')
        self.from_string(str_representation)

    def load(self, user_id: str) -> None:
        self.user_id = user_id
        os.makedirs(self._get_folder(), exist_ok=True)

        if os.path.exists(self._get_filename()):
            self._load(self._get_filename())
            self._unpack()
        else:
            self._first_time_init()

    def save(self) -> None:
        os.makedirs(self._get_folder(), exist_ok=True)
        self._pack()
        self._save(self._get_filename())
        self._unpack()


def get_html_for_clothes_set(clothes_set: ClothesSet) -> str:
    assert isinstance(clothes_set, ClothesSet)
    html = 'Предложение надеть следующие вещи:\n'
    for zone_name, zone in zip(ZONES_NAMES_RU, clothes_set.zones):
        # should replace this with some function from russian language
        if zone_name == 'голова':
            zone_name = 'голову'
        html += 'На {}: \t'.format(zone_name)
        # html += ', '.join(map(lambda clothing_item_id: get_clothing_item_name(clothing_item_id), list(zone)))
        clothes_names_to_print = []
        for clothing_item_id in zone:
            clothing_item_name = get_clothing_item_name(clothing_item_id)
            wearing_degree = clothes_set[clothing_item_id]
            clothing_item_number = get_number(clothing_item_name)
            clothing_item_gender = get_gender(clothing_item_name)
            if clothing_item_number == 'plur':
                clothing_item_gender = None

            if wearing_degree == WEARING_DEGREE_NONE:
                continue
            elif wearing_degree == WEARING_DEGREE_AVERAGE:
                clothes_names_to_print.append(clothing_item_name)
            else:
                name_to_print = clothing_item_name
                wearing_degree_to_print = set_word(WEARING_DEGREES_RU[wearing_degree], case='nomn',
                                                   number=clothing_item_number, gender=clothing_item_gender)
                clothes_names_to_print.append('{0} {1}'.format(wearing_degree_to_print, name_to_print))
        html += ', '.join(clothes_names_to_print)
        html += '\n'
    return html


def get_html_for_wardrobe(wardrobe: Wardrobe) -> str:
    """ Returns the html representation of wardrobe content"""
    assert isinstance(wardrobe, Wardrobe)
    html = '<b>Ваш Гардероб:</b>\n'
    zones_names = ['ступней', 'ног', 'торса', 'головы', 'рук']
    for zone_name, zone in zip(zones_names, wardrobe.zones):
        # should replace this with some function from russian language
        html += 'Для {}: \t'.format(zone_name)

        html += ', '.join(map(lambda clothing_item_id: get_clothing_item_name(clothing_item_id), list(zone)))
        html += '\n'
    return html
