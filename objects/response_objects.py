import sys; sys.path.insert(0, '..')

from objects.weather_forecast import WeatherForecast
from objects.storage_indicators import _DropKwargs, _StoresDate, _StoresPlace, _StoresDaytimeId, _StoresSubscriptionService
from objects.storage_indicators import _StoresSubscriptionPeriod, _StoresZoneId, _StoresFeedback, _StoresZoneFeedback
from objects.storage_indicators import _StoresClothingItemId, _StoresClothesSet, _StoresText, _StoresWardrobe
from objects.clothes import ClothesSet, Wardrobe
from objects.subscription import Subscriptions


class ResponseObject:
    """ base class for all the responses-objects """
    def __init__(self, *args, **kwargs):
        super(ResponseObject, self).__init__(*args, **kwargs)


class CommonApprove(ResponseObject):
    """ class-response, expressing the common approval """
    def __init__(self, *args, **kwargs):
        super(CommonApprove, self).__init__(*args, **kwargs)


class CommonMessage(ResponseObject, _StoresText):
    """ class-response, that simply delivers the message """
    def __init__(self, text=''):
        kwargs = locals()
        kwargs.pop('self')
        super(CommonMessage, self).__init__(**kwargs)


class ErrorUnableToParseMessage(ResponseObject, _StoresText):
    """ class-response, that gets generated if the bot was unable to parse the message """
    def __init__(self, text=''):
        kwargs = locals()
        kwargs.pop('self')
        super(ErrorUnableToParseMessage, self).__init__(**kwargs)


class ErrorUnableToProcessRequest(ResponseObject):
    """
        class-response, that gets generated if the bot was able to parse
        the message, but could not perform the understood task
    """
    def __init__(self, request_object_understood):
        self.request_object_understood = request_object_understood
        super(ErrorUnableToProcessRequest, self).__init__()


class TellWeatherForecast(ResponseObject):
    """ class-response, that stores the weather forecast for a given day """
    def __init__(self, weather_forecast: WeatherForecast) -> None:
        assert isinstance(weather_forecast, WeatherForecast)
        self.weather_forecast = weather_forecast


# class ClothesSuggestion(_StoresClothingItems):
#     ''' class-response, that suggests some clothes-set '''
#     def __init__(self, clothing_item_ids):
#         kwargs = locals(); kwargs.pop('self')
#         super(ClothesSuggestion, self).__init__(**kwargs)


class ClothesSuggestion(ResponseObject, _StoresClothesSet):
    """ class-response, that suggests some clothes-set """
    def __init__(self, clothes_set: ClothesSet):
        kwargs = locals()
        kwargs.pop('self')
        super(ClothesSuggestion, self).__init__(**kwargs)


class ReclamationReply(ResponseObject, _StoresClothesSet, _StoresFeedback):
    """ 
        class-response, that is thrown after the changes made to some clothes items for a given zone
        can optionally store the warmth-score for the new set, as the forecast should be in the context
    """
    def __init__(self, clothes_set, feedback):
        kwargs = locals(); kwargs.pop('self')
        super(ReclamationReply, self).__init__(**kwargs)


class SuccessfulSubscription(CommonApprove, _StoresText):
    """ class response, that indicates the successful subscription"""
    def __init__(self, text: str):
        """ text stores the service_name"""
        kwargs = locals(); kwargs.pop('self')
        super(SuccessfulSubscription, self).__init__(**kwargs)


class SuccessfulUnsubscription(CommonApprove, _StoresText):
    """ class response, that indicates the successful unsubscription"""
    def __init__(self, text: str):
        """ text stores the service_name"""
        kwargs = locals(); kwargs.pop('self')
        super(SuccessfulUnsubscription, self).__init__(**kwargs)


class WardrobeItemIdAdded(CommonApprove, _StoresClothingItemId):
    """ class-response, that indicates the successful add-operation to the wardrobe"""
    def __init__(self, clothing_item_id):
        kwargs = locals(); kwargs.pop('self')
        super(WardrobeItemIdAdded, self).__init__(**kwargs)


class WardrobeItemIdRemoved(CommonApprove, _StoresClothingItemId):
    """ class-response, that indicates the successful remove-operation off the wardrobe"""
    def __init__(self, clothing_item_id):
        kwargs = locals(); kwargs.pop('self')
        super(WardrobeItemIdRemoved, self).__init__(**kwargs)


class WardrobeShowResponse(ResponseObject, _StoresWardrobe):
    """ class-response, that shows the whole wardrobe content """
    def __init__(self, wardrobe: Wardrobe):
        kwargs = locals(); kwargs.pop('self')
        super(WardrobeShowResponse, self).__init__(**kwargs)


class RefineRequest(ResponseObject, _StoresText):
    """ class-response, that is generated when something needs to be refined :) """
    def __init__(self, text):
        kwargs = locals(); kwargs.pop('self')
        super(RefineRequest, self).__init__(**kwargs)


class ShowSubscriptionsResponse(ResponseObject):
    """ class-response, that serves back the subscriptions list to the user """
    def __init__(self, subscriptions: Subscriptions):
        self.subscriptions: Subscriptions = subscriptions
        super(ShowSubscriptionsResponse, self).__init__()


class FeedbackRequest(ResponseObject, _StoresPlace, _StoresDate, _StoresDaytimeId):
    """
        class-response, that is generated, when bot is interested in the score of the clothes-set for some time
        clothes are assumed to be the suggested ones
    """
    def __init__(self, place, date, daytime_id):
        kwargs = locals(); kwargs.pop('self')
        super(FeedbackRequest, self).__init__(**kwargs)
