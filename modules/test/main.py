import sys; sys.path.insert(0, '../..')

from modules.parse_message import parse_message
from modules.processing_module import process_request_objects
from modules.actions_generator import generate_actions
from modules.test.performer import do_actions
from objects.request_objects import RequestObject
from objects.context import Context
from typing import List

if __name__ == '__main__':
    print('tester here.')
    user_id = '000000000'
    print('user_id is {}'.format(user_id))
    chat_id = '0'

    while True:
        message = input('input your message: ')
        if message == 'context':
            print(Context(user_id))
            continue

        print('REQUEST OBJECTS.. ', end='')
        request_objects: List[RequestObject] = parse_message(message, user_id)
        print('ok')
        for request_object in request_objects:
            print(request_object.__class__.__name__, '\n', request_object.__dict__)
            print('---')
        print('REQUEST OBJECTS DONE\n\n')

        print('RESPONSE OBJECTS.. ', end='')
        response_objects = process_request_objects(request_objects, user_id)
        print('ok')
        for response_object in response_objects:
            print(response_object.__class__.__name__, '\n', response_object.__dict__)
            print('---')
        print('RESPONSE OBJECTS DONE\n\n')

        print('ACTIONS.. ', end='')
        actions = generate_actions(response_objects)
        print('ok')
        for action in actions:
            print(action.__class__.__name__, '\n', action.__dict__)
            print('---')
        print('ACTIONS OBJECTS DONE\n\n')

        print('PERFORMER:')
        do_actions(actions, bot=None, chat_id=chat_id)
        print('PERFORMER DONE\n\n')
