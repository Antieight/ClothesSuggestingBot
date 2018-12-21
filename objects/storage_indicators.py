import sys; sys.path.insert(0, '..')
import datetime


from constants.daytime_constants import *
from constants.services_constants import *
from constants.feedback_constants import *
from objects.clothes import ClothesSet, Wardrobe, is_valid_clothing_item_id, is_valid_zone_id


class _DropKwargs(object):
    def __init__(self, **kwargs):
        pass


class _StoresDate(_DropKwargs):
    def __init__(self, date: datetime.date, **kwargs) -> None:
        assert isinstance(date, datetime.date)
        self.date = date
        super(_StoresDate, self).__init__(**kwargs)


class _StoresPlace(_DropKwargs):
    def __init__(self, place: str, **kwargs) -> None:
        assert isinstance(place, str)
        self.place = place
        super(_StoresPlace, self).__init__(**kwargs)


class _StoresDaytimeId(_DropKwargs):
    def __init__(self, daytime_id: int, **kwargs) -> None:
        assert is_valid_daytime_id(daytime_id)
        self.daytime_id = daytime_id
        super(_StoresDaytimeId, self).__init__(**kwargs)


class _StoresSubscriptionService(_DropKwargs):
    def __init__(self, service_id: int, **kwargs) -> None:
        assert is_valid_service_id(service_id)
        self.service_id = service_id
        super(_StoresSubscriptionService, self).__init__(**kwargs)


class _StoresSubscriptionPeriod(_DropKwargs):
    def __init__(self, period: int, **kwargs) -> None:
        """ period can be an integer. semantics is the number of days """
        self.period = period
        super(_StoresSubscriptionPeriod, self).__init__(**kwargs)


class _StoresZoneId(_DropKwargs):
    def __init__(self, zone_id: int, **kwargs) -> None:
        assert is_valid_zone_id(zone_id)
        self.zone_id = zone_id
        super(_StoresZoneId, self).__init__(**kwargs)


class _StoresFeedback(_DropKwargs):
    def __init__(self, feedback: FeedbackType, **kwargs) -> None:
        assert is_valid_feedback(feedback)
        self.feedback = feedback
        super(_StoresFeedback, self).__init__(**kwargs)


class _StoresZoneFeedback(_DropKwargs):
    def __init__(self, zone_feedback: ZoneFeedbackType, **kwargs) -> None:
        assert is_valid_zone_feedback(zone_feedback)
        self.zone_feedback = zone_feedback
        super(_StoresZoneFeedback, self).__init__(**kwargs)


class _StoresClothingItemId(_DropKwargs):
    def __init__(self, clothing_item_id: int, **kwargs) -> None:
        assert is_valid_clothing_item_id(clothing_item_id)
        self.clothing_item_id = clothing_item_id
        super(_StoresClothingItemId, self).__init__(**kwargs)


# class _StoresClothingItems(_DropKwargs):
#     def __init__(self, clothing_item_ids, **kwargs):
#         for el in clothing_item_ids:
#             assert is_valid_clothing_item_id(el)
#         self.clothing_item_ids = clothing_item_ids
#         super(_StoresClothingItems, self).__init__(**kwargs)


class _StoresClothesSet(_DropKwargs):
    def __init__(self, clothes_set: ClothesSet, **kwargs) -> None:
        assert isinstance(clothes_set, ClothesSet)
        self.clothes_set = clothes_set
        super(_StoresClothesSet, self).__init__(**kwargs)


class _StoresText(_DropKwargs):
    def __init__(self, text: str, **kwargs) -> None:
        assert isinstance(text, str)
        self.text = text
        super(_StoresText, self).__init__(**kwargs)


class _StoresWardrobe(_DropKwargs):
    def __init__(self, wardrobe: Wardrobe, **kwargs) -> None:
        assert isinstance(wardrobe, Wardrobe)
        self.wardrobe = wardrobe
        super(_StoresWardrobe, self).__init__(**kwargs)
