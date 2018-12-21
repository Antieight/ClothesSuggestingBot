import os, sys; sys.path.insert(0, '../..')

from objects.context import Context
from typing import List, Optional
from objects.request_objects import *
from objects.response_objects import *
from modules.common_extractors import *
from objects.subscription import Subscriptions


# Let there be 2 states:
# initial - bot is waiting for the service id
# expecting_approval - bot sends the info and asks for the approval


def parse_message(message: str, context: Context) -> Optional[List[RequestObject]]:
    """
    Takes a message and a context and extracts a list of request objects
    :param message: the message to extract from
    :param context: the current context to look at
    :return: a list of request objects
    """
    assert isinstance(message, str)
    assert isinstance(context, Context)
    try:
        if context.safe_access('state') == 'expecting_approval':
            if extract_approval(message):
                return [ApproveAndStop()]
            context.set_info_field('state', 'initial')

        normalized_words = set(take_away_punctuation(normalize_string(message)).split())
        if len({'покажи', 'показать', 'просмотреть', 'открыть', 'посмотреть'} & normalized_words) > 0:
            return [ShowSubscriptionsRequest()]

        # if we didn't see the approval, may be user wants to edit his choice
        request_objects: List[RequestObject] = []
        if context.safe_access('state') == 'initial':
            service_id: Optional[int] = extract_subscription_service_id(message)
            period: Optional[int] = extract_subscription_period(message)
            start_date: Optional[datetime.date] = extract_date(message)
            operation_type: Optional[int] = extract_subscription_operation_type(message)
            place: Optional[str] = extract_place(message)
            if service_id is None and period is None and start_date is None and operation_type is None and place is None:
                return None
            today: datetime.date = (datetime.datetime.utcnow() + datetime.timedelta(3 / 24)).date()
            if context.safe_access('start_date') is None or start_date is not None:
                start_date = today if start_date is None else start_date
                request_objects.append(RefineDate(start_date))
            if context.safe_access('period') is None or period is not None:
                period = 1 if period is None else period
                request_objects.append(RefineSubscriptionPeriod(period))
            if context.safe_access('operation_type') is None or operation_type is not None:
                operation_type = 1 if operation_type is None else operation_type
                request_objects.append(RefineOperationType(operation_type))
            if place is not None:
                request_objects.append(RefinePlace(place=place))
            if service_id is not None:
                request_objects.append(RefineSubscriptionService(service_id))
        return request_objects
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
    response_objects: List[ResponseObject] = []
    if isinstance(request_object, ShowSubscriptionsRequest):
        subscriptions: Subscriptions = Subscriptions(context.user_id)
        context.reset()
        context.save()
        return [ShowSubscriptionsResponse(subscriptions)]

    if context.safe_access('state') == 'expecting_approval':
        if isinstance(request_object, ApproveAndStop):
            subscriptions: Subscriptions = Subscriptions(context.user_id)
            operation_type = context.safe_access('operation_type')
            service_id = context.safe_access('service_id')
            period = context.safe_access('period')
            start_date = context.safe_access('start_date')
            place = context.safe_access('place')
            service_name = 'погоду' if service_id == SERVICE_WEATHER else 'одежду'
            if operation_type == 1:
                subscriptions[service_id] = {'start_date': start_date, 'period': period, 'place': place}
                subscriptions.save()
                context.reset()
                context.save()
                return [SuccessfulSubscription(service_name)]
            elif operation_type == -1:
                subscriptions[service_id] = None
                subscriptions.save()
                context.reset()
                context.save()
                return [SuccessfulUnsubscription(service_name)]
            else:
                assert False
        else:
            context.set_info_field('state', 'initial')

    if context.safe_access('state') == 'initial':
        # we are expecting refine objects
        if isinstance(request_object, RefineDate):
            context.set_info_field('start_date', request_object.date)
        elif isinstance(request_object, RefineSubscriptionPeriod):
            context.set_info_field('period', request_object.period)
        elif isinstance(request_object, RefineSubscriptionService):
            context.set_info_field('service_id', request_object.service_id)
        elif isinstance(request_object, RefineOperationType):
            context.set_info_field('operation_type', request_object.operation_type)
        elif isinstance(request_object, RefinePlace):
            context.set_info_field('place', request_object.place)
        else:
            assert False, 'Unknown request, state is initial!'

        # loading context:
        start_date = context.safe_access('start_date')
        period = context.safe_access('period')
        service_id = context.safe_access('service_id')
        operation_type = context.safe_access('operation_type')
        place = context.safe_access('place')

        if service_id is None:
            response_objects.append(RefineRequest('На какой сервис Вы бы хотели подписаться (погода / одежда)'))
        if place is None and operation_type == 1:
            response_objects.append(RefineRequest('Для какого города Вам нужна информация?'))

        if len(response_objects):  # we have smth to refine here
            return response_objects

        if service_id is not None and (place is not None or operation_type == -1):
            # ready to ask for the approval
            service_name = 'погоду' if service_id is SERVICE_WEATHER else 'одежду'
            if operation_type == -1:
                response_message = 'Вы хотите отписаться от рассылки про {}.'.format(service_name)
            else:
                response_message = 'Вы хотите подписаться на рассылку про {0} в городе {1}. '.format(service_name,
                                                                                                     place.capitalize())
                response_message += 'Сообщения будут приходить раз в {0} дней'.format(period)
                response_message += ', начиная с {0}.'.format(start_date)
            response_objects.append(CommonMessage(response_message))
            response_message = 'Если всё верно, подтвердите, или напишите уточнения, если я что не так понял.'
            response_objects.append(CommonMessage(response_message))
            context.set_info_field('state', 'expecting_approval')
            return response_objects


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
        response_objects = process_request_object(request_object, context)
    context.save()
    return response_objects
