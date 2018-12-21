import sys; sys.path.insert(0, '../..')

from objects.context import Context
from objects.request_objects import *
from objects.response_objects import *
from objects.history_table import *
from modules.common_extractors import *
from modules.clothes_model.interface import *
from modules.weather_forecast import *


# Context.info:
# context.info['state']       - initial or generating
# when context.info['state'] is 'initial':
# we try to get the date, daytime, place
# when those are obtained we send out suggestion with score
# and context.info['state'] becomes 'generating'
# from now on we do accept the reclamations, requests to show the current clothes set/score
#
# context.info['clothes_set'] - current suggestion (stored serialized)
# context.info['history']     - list of bad zones (stored serialized)


def parse_message(message: str, context: Context) -> Optional[List[RequestObject]]:
    """
    Takes a message and a context and extracts a list of request objects
    :param message: the message to extract from
    :param context: the current context to look at
    :return: a list of request objects
    """
    assert isinstance(message, str)
    assert isinstance(context, Context)
    request_objects = list()

    try:
        if context.safe_access('state') == 'initial':
            date = extract_date(message)
            place = extract_place(message)
            daytime_id = extract_daytime_id(message)
            if date is not None:
                request_objects.append(RefineDate(date=date))
            if place is not None:
                request_objects.append(RefinePlace(place=place))
            if daytime_id is not None:
                request_objects.append(RefineDaytimeId(daytime_id=daytime_id))
            if daytime_id is None and place is None and date is None:
                return None
            return request_objects
        elif context.safe_access('state') == 'generating':
            # here we have to subclassify the message
            # it can be either some simple request
            # like to Show what we got or, the score, or even to accept it
            # There can be a reclamation to a specific zone as well
            # And some clothes might be specified as well
            show_indicators = {'показать', 'покажи', 'получаться', 'получается', 'текущий', 'сейчас'}
            show_indicators = show_indicators | set(map(normalize_string, show_indicators))
            words = set(normalize_string(take_away_punctuation(message)).split())
            words = words | set(take_away_punctuation(message).split())
            if len(words & show_indicators) > 0:
                score_indicators = {'score', 'показатель', 'рейтинг', 'скор', 'оценка'}
                clothes_set_indicators = {'набор', 'одежда', 'что', 'как'}
                if len(words & clothes_set_indicators) > 0:
                    request_objects.append(ShowCurrentClothesSetChoice())
                if len(words & score_indicators) > 0:
                    request_objects.append(ShowCurrentClothesSetScore())
                if len(request_objects) > 0:
                    return request_objects

            if extract_approval(message):
                request_objects.append(ClothesSetApproveAndStop())
                return request_objects

            zone_id = extract_zone_id(message)
            clothes_set = extract_clothes_set(message)

            if zone_id is not None and clothes_set is not None:
                request_objects.append(ReclamationOnClothesSetOfferingOwnSuggestion(zone_id, clothes_set))
            elif zone_id is not None:
                request_objects.append(ReclamationOnClothesSetOffering(zone_id))
            else:
                return None
            return request_objects
        else:
            assert False, 'unknown state'
    except Exception:
        return None


def process_request_object(request_object: RequestObject, context: Context) -> List[ResponseObject]:
    """
    Takes a request object and a context and reacts to this message.
    That is changes its context and generates some response objects in return
    :param request_object:  request_object to parse
    :param context: current context of the user
    :return: a list of response objects, generated in response to the given request object
    """
    response_objects = []
    if context.safe_access('state') == 'initial':
        # here we expect refines
        if isinstance(request_object, RefineDate):
            context.set_info_field('date', request_object.date)
        if isinstance(request_object, RefinePlace):
            context.set_info_field('place', request_object.place)
        if isinstance(request_object, RefineDaytimeId):
            context.set_info_field('daytime_id', request_object.daytime_id)

        date = context.safe_access('date')
        place = context.safe_access('place')
        daytime_id = context.safe_access('daytime_id')
        if date is None:
            response_objects.append(RefineRequest('На какую дату подбираем одежду?'))
        if place is None:
            response_objects.append(RefineRequest('В каком городе Вы будете?'))
        if daytime_id is None:
            response_objects.append(RefineRequest('На какое время дня вам нужно подобрать одежду?'))
        if len(response_objects):
            # we still need something to refine
            return response_objects

        # everything is refined!
        context.set_info_field('state', 'generating')
        weather_forecast: WeatherForecast = get_weather_forecast(place=place, dates=[date])
        forecast_frame: ForecastFrame = weather_forecast[date][daytime_id]
        clothes_set: ClothesSet = generate_clothes_set(forecast_frame, context.user_id)
        context.set_info_field('clothes_set', clothes_set.to_string())
        context.set_info_field('forecast_frame', forecast_frame.to_string())
        context.save()
        response_objects.append(ClothesSuggestion(clothes_set))
        return response_objects
    elif context.safe_access('state') == 'generating':
        # here we expect Show-something requests
        # accept and stop request
        # reclamations

        # getting context.info objects..
        clothes_set_str: str = context.safe_access('clothes_set')
        clothes_set: ClothesSet = ClothesSet.create_from_string(clothes_set_str)

        forecast_frame_str: str = context.safe_access('forecast_frame')
        forecast_frame = ForecastFrame.create_from_string(forecast_frame_str)

        if isinstance(request_object, ShowCurrentClothesSetChoice):
            response_objects.append(ClothesSuggestion(clothes_set))
        if isinstance(request_object, ShowCurrentClothesSetScore):
            score = get_score(clothes_set, forecast_frame, context.user_id)
            text = 'Оценка текущего набора: {}'.format(score)
            response_objects.append(CommonMessage(text))
        if isinstance(request_object, ClothesSetApproveAndStop):
            pending_history_table = UserPendingHistoryTable(context.user_id)
            pending_history_table.add_history_record(HistoryRecord(clothes_set=clothes_set, zones_scores=[0]*len(ZONES),
                                                                   forecast_frame=forecast_frame))
            pending_history_table.save()
            context.reset()
            context.save()
            response_objects.append(CommonApprove())
        if isinstance(request_object, ReclamationOnClothesSetOffering):
            zone_id = request_object.zone_id
            clothes_set = regenerate_zone(zone_id, forecast_frame, clothes_set, context.user_id)
            response_objects.append(CommonApprove())
            response_objects.append(ClothesSuggestion(clothes_set))
        if isinstance(request_object, ReclamationOnClothesSetOfferingOwnSuggestion):
            zone_id = request_object.zone_id
            zone_clothes_set = request_object.clothes_set
            for clothing_item_id in get_clothing_items_ids_by_zone(zone_id):
                clothes_set.take_off(clothing_item_id)
            for clothing_item_id in zone_clothes_set.zones[zone_id]:
                clothes_set.wear(clothing_item_id, zone_clothes_set[clothing_item_id])
            response_objects.append(CommonApprove())
            response_objects.append(ClothesSuggestion(clothes_set))

        context.set_info_field('clothes_set', clothes_set.to_string())
        context.set_info_field('forecast_frame', forecast_frame.to_string())
        context.save()
        return response_objects
    else:
        assert False, "unknown state"


def process_request_objects(request_objects: List[RequestObject], context: Context) -> List[ResponseObject]:
    """
    Takes a list of request objects,
    reacts to each of them with process_request_object(...)
    and merges these lists together and returns it
    :param request_objects: the request objects to parse
    :param context: current context of the user
    :return: a list of response objects, generated in response to the given request objects
    """
    response_objects = []
    for request_object in request_objects:
        # we store just the last response_objects (the most relevant)
        response_objects = process_request_object(request_object, context)
    context.save()
    return response_objects
