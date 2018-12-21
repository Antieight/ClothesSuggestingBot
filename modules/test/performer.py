import os, sys; sys.path.insert(0, '../..')

from objects.action import PrintAction, ShowImage, ShowPoll, Action
from typing import Any, Iterable


def do_action(action: Action, bot: Any, chat_id: str) -> None:
    """ Accepts an action and performs it with bot, using chat with chat_id"""
    if isinstance(action, PrintAction):
        print('PrintAction(text={0}, chat_id={1})'.format(action.text, chat_id))
    elif isinstance(action, ShowImage):
        print('ShowImage(image_name={0}, caption={1}, chat_id={2}'.format(action.image_name, action.caption, chat_id))
    elif isinstance(action, ShowPoll):
        print('ShowPoll(title={0}, options={1}, chat_id={2})'.format(action.title, action.options, chat_id))
    else:
        assert False, 'Unknown Action encountered'


def do_actions(actions: Iterable[Action], bot: Any, chat_id: str) -> None:
    """
        Accepts a list (or any other iterable) of actions (subclass of Action)
        and performs them with bot, using chat with chat_id
    """
    for action in actions:
        do_action(action, bot, chat_id)
