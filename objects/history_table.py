import sys; sys.path.insert(0, '..')
import pandas as pd
import datetime

from objects.clothes import *
from objects.weather_forecast import ForecastFrame
from constants.global_constants import USERS_PATH
from constants.feedback_constants import *
from typing import Optional


TABLE_COLUMNS = [*['clothing_item_{}'.format(clothing_item_name) 
                   for clothing_item_name in get_clothing_items_names()],
                 *['score_{}'.format(zone_name) for zone_name in get_zones_names()],
                 *['forecast_frame_{}'.format(key_) for key_ in ForecastFrame().__dict__.keys()]]


class HistoryRecord:
    """
        Stores one record of user activity,
        That is his clothes_set, the weather for that day (ForecastFrame)
        and the feedback, we have received
    """
    def __init__(self, clothes_set: ClothesSet = None, zones_scores: ZoneFeedbackType = None,
                 forecast_frame: ForecastFrame = None) -> None:
        self.clothes_set = self.zones_scores = self.forecast_frame = None
        self.set_clothes_set(clothes_set=clothes_set)
        self.set_zones_scores(zones_scores=zones_scores)
        self.set_forecast_frame(forecast_frame=forecast_frame)

    def get_clothes_set(self) -> ClothesSet:
        return self.clothes_set

    def get_zones_scores(self) -> ZoneFeedbackType:
        return self.zones_scores

    def get_forecast_frame(self) -> ForecastFrame:
        return self.forecast_frame

    def get_date(self) -> datetime.date:
        return self.forecast_frame.date
    
    def get_place(self) -> str:
        return self.forecast_frame.place
    
    def set_clothes_set(self, clothes_set: ClothesSet = None) -> None:
        assert clothes_set is None or isinstance(clothes_set, ClothesSet)
        self.clothes_set = clothes_set
    
    def set_forecast_frame(self, forecast_frame: ForecastFrame = None) -> None:
        assert forecast_frame is None or isinstance(forecast_frame, ForecastFrame)
        self.forecast_frame = forecast_frame
    
    def set_zones_scores(self, zones_scores: ZoneFeedbackType = None) -> None:
        if zones_scores is not None:
            assert len(zones_scores) == len(ZONES)
            assert min(zones_scores) in range(-5, 6)
            assert max(zones_scores) in range(-5, 6)
        self.zones_scores = zones_scores

    @staticmethod
    def from_dict(params_dict: dict):
        assert set(params_dict.keys()) == set(TABLE_COLUMNS)

        def extract_prefixed_dict(dicti, prefix):
            return {key[len(prefix):]: val for key, val in dicti.items() if str(key).startswith(prefix)}
        forecast_frame_items = extract_prefixed_dict(params_dict, prefix='forecast_frame_')
        clothing_items = extract_prefixed_dict(params_dict, prefix='clothing_item_')
        scores_items = extract_prefixed_dict(params_dict, prefix='score_')
        clothes_set = ClothesSet()
        for clothing_item_name, wearing_degree_id in clothing_items.items():
            clothes_set.wear(clothing_item_name, wearing_degree_id=int(wearing_degree_id))
        forecast_frame_items['date'] = eval(forecast_frame_items['date'])
        forecast_frame = ForecastFrame(**forecast_frame_items)
        zones_scores = [0]*len(ZONES)
        for key, value in scores_items.items():
            zones_scores[ZONES_NAMES_RU.index(key)] = value
        return HistoryRecord(clothes_set=clothes_set, zones_scores=zones_scores, 
                             forecast_frame=forecast_frame)

    def to_dict(self) -> dict:
        params_dict = {key: None for key in TABLE_COLUMNS}
        params_dict.update({'clothing_item_{}'.format(clothing_item_name): self.clothes_set[clothing_item_name]
                            for clothing_item_name in get_clothing_items_names()})
        params_dict.update({'forecast_frame_{}'.format(key): value
                            for key, value in self.forecast_frame.__dict__.items()})
        params_dict.update({'score_{}'.format(ZONES_NAMES_RU[key]): self.zones_scores[key]
                            for key in range(len(ZONES))})
        params_dict['forecast_frame_date'] = params_dict['forecast_frame_date'].__repr__()
        return params_dict


class HistoryTable:
    def __init__(self, history_records):
        """ accepts a list of (HistoryRecord)s """
        self.history_records = []
        for history_record in history_records:
            self.add_history_record(history_record)
    
    def add_history_record(self, history_record):
        assert isinstance(history_record, HistoryRecord)
        self.history_records.append(history_record)

    @staticmethod
    def from_dataframe(history_df: pd.DataFrame):
        pre_history_records = history_df.to_dict(orient='index')
        # doesn't work for empty dataframes. may be fix later
        # assert len(pre_history_records) == max(list(pre_history_records.keys())) + 1
        history_records = [pre_history_records[i] for i in range(len(pre_history_records))]
        for ind, pre_history_record in enumerate(history_records):
            history_records[ind] = HistoryRecord.from_dict(pre_history_record)
        return HistoryTable(history_records)

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(list(map(HistoryRecord.to_dict, self.history_records)))

    def __getitem__(self, index: int) -> HistoryRecord:
        return self.history_records[index]

    @property
    def size(self) -> int:
        return len(self.history_records)


class UserHistoryTable:
    def __init__(self, user_id: str) -> None:
        self.user_id: Optional[str] = None
        self.history_table: Optional[HistoryTable] = None
        self.load(user_id)

#     # maybe enable the autosave at destruction
#     def __del__(self):
#         self.save()

    def _get_folder(self):
        return os.path.join(USERS_PATH, self.user_id)

    def _get_filename(self):
        return os.path.join(self._get_folder(), 'history.csv')

    def get_dataframe_representation(self):
        """
            Returns the inner representation as a dataframe.
            Changing it will not affect the state of the table
        """
        return self.history_table.to_dataframe()
    
    def add_history_record(self, history_record: HistoryRecord) -> None:
        self.history_table.add_history_record(history_record=history_record)

    def get_history_table(self) -> HistoryTable:
        return self.history_table

    def __getitem__(self, index: int) -> HistoryRecord:
        return self.history_table[index]

    @property
    def size(self) -> int:
        return self.history_table.size

    def load(self, user_id: str) -> None:
        self.user_id = user_id
        os.makedirs(self._get_folder(), exist_ok=True)

        if os.path.exists(self._get_filename()):
            history_df = pd.read_csv(self._get_filename(), index_col=0)
            history_df = history_df.where(pd.notnull(history_df), None)
        else:
            history_df = pd.DataFrame(columns=TABLE_COLUMNS)
        self.history_table = HistoryTable.from_dataframe(history_df)

    def save(self) -> None:
        os.makedirs(self._get_folder(), exist_ok=True)
        history_df = self.history_table.to_dataframe()
        history_df.to_csv(path_or_buf=self._get_filename())


class UserPendingHistoryTable(UserHistoryTable):
    def __init__(self, user_id: str) -> None:
        super(UserPendingHistoryTable, self).__init__(user_id)

    def _get_filename(self) -> str:
        return os.path.join(self._get_folder(), 'pending_history.csv')
