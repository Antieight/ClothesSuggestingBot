import sys; sys.path.insert(0, '..')
import os

from objects.action import PrintAction, ShowImage, ShowPoll, Action
from constants.global_constants import TEMP_PATH
from typing import Any, Iterable


def send_message(message: str, bot: Any, chat_id: str) -> None:
    """
        Wrapper of bot functionality.
        Sends the given message to the chat with the given chat_id, using the passed bot
    """
    bot.send_message(chat_id, message, parse_mode='HTML')


def show_image(image_name: str, caption: str, bot: Any, chat_id: str) -> Any:
    """
        Wrapper of bot functionality.
        Shows the image, that is located at TEMP_PATH/image_name. Show the caption below the image.
        Uses bot to perform this. The image is show to the chat with chat_id.
    """
    image_path = os.path.join(TEMP_PATH, image_name)
    bot.send_photo(chat_id, open(image_path, 'rb'), caption, parse_mode='HTML')


def show_poll(title: str, options: Iterable[str], bot: Any, chat_id: str) -> Any:
    """
        Wrapper of bot functionality
        Shows the poll with the given title and options to the chat with chat_id, using the passed bot
    """
    raise NotImplementedError


def do_action(action: Action, bot: Any, chat_id: str) -> None:
    """ Accepts an action and performs it with bot, using chat with chat_id"""
    if isinstance(action, PrintAction):
        send_message(action.text, bot, chat_id)
    elif isinstance(action, ShowImage):
        show_image(image_name=action.image_name, caption=action.caption, bot=bot, chat_id=chat_id)
    elif isinstance(action, ShowPoll):
        show_poll(title=action.title, options=action.options, bot=bot, chat_id=chat_id)
    else:
        assert False, 'Unknown Action encountered'


def do_actions(actions: Iterable[Action], bot: Any, chat_id: str) -> None:
    """
        Accepts a list (or any other iterable) of actions (subclass of Action)
        and performs them with bot, using chat with chat_id
    """
    for action in actions:
        do_action(action, bot, chat_id)
