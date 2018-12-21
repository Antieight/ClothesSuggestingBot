"""
This module is a sort of a heap of useful functions,
for which no separate module can logically be created
"""
import os, sys; sys.path.insert(0, '..')
from constants.global_constants import *


def write_chat_id(user_id: str, chat_id: str) -> None:
    """
    Creates a file chat_id.txt in user's directory, that contains the user's chat_id
    This file is needed to send to a user messages at bot's own will
    For instance he might want to ask for a feedback or to send out some subscription letters
    :param user_id: the id of user, for which we store the chat_id
    :param chat_id: user's current chat_id
    :return: None
    """
    current_user_path: str = os.path.join(USERS_PATH, user_id, 'chat_id.txt')
    with open(current_user_path, 'w') as chat_id_file:
        chat_id_file.write(chat_id)
