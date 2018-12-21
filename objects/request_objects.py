import sys; sys.path.insert(0, '..')

import datetime
from objects.storage_indicators import _StoresDate, _StoresPlace, _StoresDaytimeId, _StoresSubscriptionService
from objects.storage_indicators import _StoresSubscriptionPeriod, _StoresZoneId, _StoresFeedback, _StoresZoneFeedback
from objects.storage_indicators import _StoresClothingItemId, _StoresClothesSet

from objects.clothes import ClothesSet
from constants.feedback_constants import *


class RequestObject:
    def __init__(self, *args, **kwargs):
        super(RequestObject, self).__init__(*args, **kwargs)


class ApproveAndStop(RequestObject):
    def __init__(self, *args, **kwargs):
        super(ApproveAndStop, self).__init__(*args, **kwargs)


class CancelRequest(RequestObject):
    """ this type of request allows to reset the context immediately. No parsers and extractors are run"""
    def __init__(self, *args, **kwargs):
        super(CancelRequest, self).__init__(*args, **kwargs)


class ShowSubscriptionsRequest(RequestObject):
    """ request-object, that means the user wants to see his subscriptions """
    def __init__(self, *args, **kwargs):
        super(ShowSubscriptionsRequest, self).__init__(*args, **kwargs)


class Nonsense(RequestObject):
    def __init__(self, *args, **kwargs):
        super(Nonsense, self).__init__(*args, **kwargs)


class WeatherRequest(RequestObject, _StoresDate, _StoresPlace):
    def __init__(self, place: str, date: datetime.date) -> None:
        kwargs = locals()
        kwargs.pop('self')
        super(WeatherRequest, self).__init__(**kwargs)


class SubscribeRequest(RequestObject, _StoresSubscriptionService, _StoresSubscriptionPeriod, _StoresDate):
    def __init__(self, service_id: int, period: int, date: datetime.date) -> None:
        kwargs = locals()
        kwargs.pop('self')
        super(SubscribeRequest, self).__init__(**kwargs)


class ClothesSetRequest(RequestObject, _StoresDate, _StoresPlace, _StoresDaytimeId):
    def __init__(self, date: datetime.date, place: str, daytime_id: int) -> None:
        kwargs = locals()
        kwargs.pop('self')
        super(ClothesSetRequest, self).__init__(**kwargs)


class ReclamationOnClothesSetOffering(RequestObject, _StoresZoneId):
    def __init__(self, zone_id: int) -> None:
        kwargs = locals()
        kwargs.pop('self')
        super(ReclamationOnClothesSetOffering, self).__init__(**kwargs)


class ReclamationOnClothesSetOfferingOwnSuggestion(RequestObject, _StoresZoneId, _StoresClothesSet):
    def __init__(self, zone_id: int, clothes_set: ClothesSet) -> None:
        kwargs = locals()
        kwargs.pop('self')
        super(ReclamationOnClothesSetOfferingOwnSuggestion, self).__init__(**kwargs)


class ShowCurrentClothesSetChoice(RequestObject):
    def __init__(self, *args, **kwargs):
        super(ShowCurrentClothesSetChoice, self).__init__(*args, **kwargs)


class ShowCurrentClothesSetScore(RequestObject):
    def __init__(self, *args, **kwargs):
        super(ShowCurrentClothesSetScore, self).__init__(*args, **kwargs)


class ClothesSetApproveAndStop(RequestObject):
    def __init__(self, *args, **kwargs):
        super(ClothesSetApproveAndStop, self).__init__(*args, **kwargs)


class WardrobeAddClothingItemId(RequestObject, _StoresClothingItemId):
    def __init__(self, clothing_item_id: int):
        kwargs = locals()
        kwargs.pop('self')
        super(WardrobeAddClothingItemId, self).__init__(**kwargs)


class WardrobeRemoveClothingItemId(RequestObject, _StoresClothingItemId):
    def __init__(self, clothing_item_id: int) -> None:
        kwargs = locals()
        kwargs.pop('self')
        super(WardrobeRemoveClothingItemId, self).__init__(**kwargs)


class WardrobeShow(RequestObject):
    def __init__(self, *args, **kwargs) -> None:
        super(WardrobeShow, self).__init__(*args, **kwargs)


class CommonFeedback(RequestObject, _StoresFeedback):
    def __init__(self, feedback: FeedbackType) -> None:
        kwargs = locals()
        kwargs.pop('self')
        super(CommonFeedback, self).__init__(**kwargs)


class ZoneFeedback(RequestObject, _StoresZoneFeedback):
    def __init__(self, zone_feedback: ZoneFeedbackType) -> None:
        kwargs = locals()
        kwargs.pop('self')
        super(ZoneFeedback, self).__init__(**kwargs)


class ClothesSpecification(RequestObject, _StoresClothesSet):
    def __init__(self, clothes_set: ClothesSet) -> None:
        kwargs = locals()
        kwargs.pop('self')
        super(ClothesSpecification, self).__init__(**kwargs)


class RefineDate(RequestObject, _StoresDate):
    def __init__(self, date: datetime.date) -> None:
        kwargs = locals()
        kwargs.pop('self')
        super(RefineDate, self).__init__(**kwargs)


class RefineClothesObject(RequestObject, _StoresClothingItemId):
    def __init__(self, clothing_item_id: int) -> None:
        kwargs = locals()
        kwargs.pop('self')
        super(RefineClothesObject, self).__init__(**kwargs)


class RefinePlace(RequestObject, _StoresPlace):
    def __init__(self, place: str) -> None:
        kwargs = locals()
        kwargs.pop('self')
        super(RefinePlace, self).__init__(**kwargs)


class RefineSubscriptionService(RequestObject, _StoresSubscriptionService):
    def __init__(self, service_id: int) -> None:
        kwargs = locals()
        kwargs.pop('self')
        super(RefineSubscriptionService, self).__init__(**kwargs)


class RefineSubscriptionPeriod(RequestObject, _StoresSubscriptionPeriod):
    def __init__(self, period: int) -> None:
        kwargs = locals()
        kwargs.pop('self')
        super(RefineSubscriptionPeriod, self).__init__(**kwargs)


class RefineZoneId(RequestObject, _StoresZoneId):
    def __init__(self, zone_id):
        kwargs = locals()
        kwargs.pop('self')
        super(RefineZoneId, self).__init__(**kwargs)


class RefineFeedback(RequestObject, _StoresFeedback):
    def __init__(self, feedback: FeedbackType) -> None:
        kwargs = locals()
        kwargs.pop('self')
        super(RefineFeedback, self).__init__(**kwargs)


class RefineZoneFeedback(RequestObject, _StoresZoneFeedback):
    def __init__(self, zone_feedback: ZoneFeedbackType) -> None:
        kwargs = locals()
        kwargs.pop('self')
        super(RefineZoneFeedback, self).__init__(**kwargs)


class RefineDaytimeId(RequestObject, _StoresDaytimeId):
    def __init__(self, daytime_id: int) -> None:
        kwargs = locals()
        kwargs.pop('self')
        super(RefineDaytimeId, self).__init__(**kwargs)


class RefineOperationType(RequestObject):
    """
    Operation type serves for storing, whether the user wants to subscribe/unsubscribe,
    or add/delete to the wardrobe. -1 -- unsubscribe/delete; 1 -- subscribe/add
    """

    def __init__(self, operation_type: int, *args, **kwargs) -> None:
        assert operation_type in (-1, 1)
        self.operation_type: int = operation_type
        super(RefineOperationType, self).__init__(*args, **kwargs)
