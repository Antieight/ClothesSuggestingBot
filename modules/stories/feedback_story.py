import os, sys; sys.path.insert(0, '../..')

from objects.context import Context
from objects.request_objects import *
from objects.response_objects import *
from objects.history_table import *
from modules.common_extractors import *
from typing import List, Optional


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
        # what we need is either zones_score or just a score.
        # so..
        zones_feedback = extract_zones_feedback(message)
        feedback = extract_feedback(message)
        if zones_feedback is not None:
            return [RefineZoneFeedback(zones_feedback)]
        elif feedback is not None:
            return [RefineFeedback(feedback)]
        else:
            return None
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
    # getting zones_feedback out of request object
    if isinstance(request_object, RefineFeedback):
        feedback = request_object.feedback
        zones_feedback = [feedback] * len(ZONES)
    elif isinstance(request_object, RefineZoneFeedback):
        zones_feedback = request_object.zone_feedback
    else:
        assert False, "Unknown request_object, shouldn't have gotten here"

    pending_history_table: UserHistoryTable = UserPendingHistoryTable(context.user_id)
    hr: HistoryRecord = pending_history_table[-1]
    hrs: List[HistoryRecord] = pending_history_table.history_table.history_records
    hrs.remove(hr)
    pending_history_table.save()

    hr.set_zones_scores(zones_feedback)

    ht: UserHistoryTable = UserHistoryTable(user_id=context.user_id)
    ht.add_history_record(hr)
    ht.save()
    context.reset()
    context.save()
    return [CommonMessage('Спасибо за отзыв! Запись занесена в историю.')]


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
