import sys; sys.path.insert(0, '..')

from modules.parse_message import STORIES_MODULES
from objects.context import Context
from typing import Type, List
from objects.request_objects import *
from objects.response_objects import *
from typing import List

"""
    This module has to accept the request-object and pass it to the correct module.
    Then wait for it to finish and then return the response-object as a result
"""


def process_request_objects(request_objects: List[RequestObject], user_id: str) -> List[ResponseObject]:
    try:
        context = Context(user_id)

        if len(request_objects) == 0:
            return [ErrorUnableToParseMessage()]

        if isinstance(request_objects[0], Nonsense):
            return [ErrorUnableToParseMessage()]

        if isinstance(request_objects[0], CancelRequest):
            context.reset()
            context.save()
            return [CommonMessage('Ок, проехали.')]

        # try:
        response_objects = STORIES_MODULES[context.get_story()].process_request_objects(request_objects, context)
        # except Exception:
        #    response_objects = [ErrorUnableToProcessRequest(str(request_objects))]

        context.save()

        return response_objects

    except Exception:
        if isinstance(request_objects, list) and len(request_objects) > 0:
            return [ErrorUnableToProcessRequest(request_objects[0].__class__.__name__)]
        else:
            return [ErrorUnableToProcessRequest(' ')]
