import os, sys; sys.path.insert(0, '../..')

from objects.context import Context
from typing import List
from objects.request_objects import *
from objects.response_objects import *
from modules.common_extractors import *
from objects.clothes import *

# the requests of this type do not require much of a context.


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
        wardrobe_operation_type = extract_wardrobe_operation(message)
        clothes_set = extract_clothes_set(message)
        if wardrobe_operation_type == 0:
            return [WardrobeShow()]
        if clothes_set is None:
            return None

        request_objects: List[RequestObject] = []
        if wardrobe_operation_type == 1:
            for clothing_item_id in clothes_set:
                request_objects.append(WardrobeAddClothingItemId(clothing_item_id))
        else:  # wardrobe_operation == -1
            for clothing_item_id in clothes_set:
                request_objects.append(WardrobeRemoveClothingItemId(clothing_item_id))
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
    # we are ignoring context, everything is stored in the request_object
    response_objects = []
    wardrobe = Wardrobe(context.user_id)
    if isinstance(request_object, WardrobeAddClothingItemId):
        wardrobe.add_item(request_object.clothing_item_id)
        response_objects.append(WardrobeItemIdAdded(request_object.clothing_item_id))
    elif isinstance(request_object, WardrobeRemoveClothingItemId):
        wardrobe.remove_item(request_object.clothing_item_id)
        response_objects.append(WardrobeItemIdRemoved(request_object.clothing_item_id))
    elif isinstance(request_object, WardrobeShow):
        response_objects.append(WardrobeShowResponse(wardrobe))
    else:
        assert False
    wardrobe.save()
    context.reset()
    context.save()
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
