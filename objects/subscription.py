import sys; sys.path.insert(0, '..')
import os
import datetime

from constants.global_constants import USERS_PATH
from constants.services_constants import is_valid_service_id, SERVICE_WEATHER, SERVICE_CLOTHES_SET
from objects.serialization import Serializable
from typing import Optional


class Subscriptions(Serializable):
    def __init__(self, user_id: str) -> None:
        self.subscriptions: Optional[dict] = {SERVICE_WEATHER: None, SERVICE_CLOTHES_SET: None}
        self.user_id: str = user_id
        self.load(user_id)

    def _first_time_init(self) -> None:
        self.subscriptions = {SERVICE_WEATHER: None, SERVICE_CLOTHES_SET: None}
        # each item in self.subscriptions should store a dict with period and start_date fields

    def __getitem__(self, service_id: int) -> Optional[dict]:
        assert is_valid_service_id(service_id)
        return self.subscriptions[service_id]

    def __setitem__(self, service_id: int, subscription_dict: Optional[dict]) -> None:
        assert is_valid_service_id(service_id)
        if subscription_dict is None:
            self.subscriptions[service_id] = None
            return
        assert isinstance(subscription_dict, dict)
        assert 'period' in subscription_dict and 'start_date' in subscription_dict and 'place' in subscription_dict
        self.subscriptions[service_id] = subscription_dict

    def _get_folder(self) -> str:
        return os.path.join(USERS_PATH, self.user_id)

    def _get_filename(self) -> str:
        return os.path.join(self._get_folder(), 'subscriptions.json')

    def _pack(self):
        """ transforms the inner data structure so that it is able to be dumped """
        for service in [SERVICE_WEATHER, SERVICE_CLOTHES_SET]:
            subscription = self[service]
            if subscription is not None:
                subscription['start_date'] = subscription['start_date'].__repr__()

    def _unpack(self) -> None:
        """ Changes inner date-fields back to the original type (the were str in packed state)"""
        for service in [SERVICE_WEATHER, SERVICE_CLOTHES_SET]:
            subscription = self[service]
            if subscription is not None:
                subscription['start_date'] = eval(subscription['start_date'])

    def save(self) -> None:
        os.makedirs(self._get_folder(), exist_ok=True)
        self._pack()
        self._save(self._get_filename())
        self._unpack()

    def load(self, user_id: str) -> None:
        self.user_id = user_id
        os.makedirs(self._get_folder(), exist_ok=True)

        if os.path.exists(self._get_filename()):
            self._load(self._get_filename())
            self.subscriptions = {int(key): value for key, value in self.subscriptions.items()}
            self._unpack()
        else:
            self._first_time_init()
