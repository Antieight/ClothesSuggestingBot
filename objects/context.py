import sys; sys.path.insert(0, '..')
import os
import datetime

from constants.stories_constants import *
from constants.global_constants import ROOT_PATH, USERS_PATH
from objects.serialization import Serializable
from typing import Any


class Context(Serializable):
    """ Context represents the current state of the conversaion between the user and out bot.
    
    Context is stored for each user and has 
    - user_id (clear)
    - story_id (story_id is the id of the action going on, such as "weather forecast request" or "wardrobe change action")
        see constants.stories_constants for more information
    - last_message_timestamp - the moment in time, when the last message was received from the user.
    - info - some dict, that contains the very context
    """
    def __init__(self, user_id):
        self.info = self.user_id = self.last_message_timestamp = self.story_id = None
        self.load(user_id)

    def _first_time_init(self):
        self.set_story(story_id=STORY_NO_STORY)  # that is None
        self.touch()
        self.set_info(None)

    def reset(self):
        self._first_time_init()

    def set_story(self, story_id):
        assert is_valid_story_id(story_id)
        self.story_id = story_id

    def get_story(self):
        return self.story_id

    def get_info(self):
        return self.info

    def safe_access(self, info_key: str):
        if info_key not in self.info:
            self.info[info_key] = None
        return self.info[info_key]

    def safe_update(self, info_key: str, info_value: Any) -> None:
        """
        Updates the info part, setting info_value for info_key key
        Does so only if info_part doesn't have not-None for info_key key
        :param info_key: key
        :param info_value: value
        :return: None
        """
        if self.safe_access(info_key) is None:
            self.info[info_key] = info_value

    def set_info_field(self, info_key: str, info_value: Any) -> None:
        self.info[info_key] = info_value

    def set_last_message_timestamp(self, last_message_timestamp=None):
        if last_message_timestamp is None:
            self.last_message_timestamp = datetime.datetime.now()
        else:
            assert isinstance(last_message_timestamp, datetime.datetime)
            self.last_message_timestamp = last_message_timestamp

    def touch(self):
        """ analogous to the UNIX command line utility """
        self.set_last_message_timestamp()

    def set_info(self, info=None):
        if info is None:
            self.info = {'state': 'initial'}
            return
        assert isinstance(info, dict)
        self.info = info

    def _get_folder(self):
        return os.path.join(USERS_PATH, self.user_id)

    def _get_filename(self):
        return os.path.join(self._get_folder(), 'context.json')

    def load(self, user_id):
        """ loads the context from the filesystem, if it exists, otherwise does the _first_time_init """
        self.user_id = user_id
        os.makedirs(self._get_folder(), exist_ok=True)

        if os.path.exists(self._get_filename()):
            self._load(self._get_filename())
            # timestamp is stored in string format as __repr__()
            self.last_message_timestamp = eval(self.last_message_timestamp)
            self.find_and_restore_the_date()
        else:
            self._first_time_init()

    def save(self):
        """ saves the context to the filesystem """
        os.makedirs(self._get_folder(), exist_ok=True)
        self.touch()
        self.last_message_timestamp = self.last_message_timestamp.__repr__()
        self.find_and_convert_the_date()
        self._save(self._get_filename())
        self.find_and_restore_the_date()
        self.last_message_timestamp = eval(self.last_message_timestamp)

    def is_obsolete(self, timeout_hours=1):
        time_delta = datetime.datetime.now() - self.last_message_timestamp
        return time_delta.seconds > timeout_hours * 3600

    def has_story(self):
        return self.story_id != STORY_NO_STORY

    def find_and_convert_the_date(self, dicti=None):
        if dicti is None:
            dicti = self.info
        for key, value in dicti.items():
            if isinstance(value, dict):
                self.find_and_convert_the_date(value)
            if isinstance(value, datetime.date):
                dicti[key] = value.__repr__()

    def find_and_restore_the_date(self, dicti=None):
        if dicti is None:
            dicti = self.info
        for key, value in dicti.items():
            if isinstance(value, dict):
                self.find_and_convert_the_date(value)
            if isinstance(value, str) and value.startswith("datetime.date"):
                dicti[key] = eval(value)
