import sys; sys.path.insert(0, '..')
import datetime
from constants.daytime_constants import *
from typing import Union, Iterable, Optional, Type, List, Dict
from json import dumps, loads
from copy import deepcopy


common_states = ['ясно', 'дождь', 'небольшой дождь', 'пасмурно', 'облачно', 
                 'облачно с прояснениями', 'малооблачно', 'снег', 'небольшой снег',
                 'дождь со снегом']


class _ChecksTypes:
    @staticmethod
    def check_type_accept_none(val, val_type: Type) -> None:
        pattern = 'expected None or {0}, got {1} instead'
        assert isinstance(val, (val_type, type(None))), pattern.format(val_type, type(val))

    @staticmethod
    def check_types_accept_none(val, val_types: Iterable[Type]) -> None:
        assert isinstance(val, (*val_types, type(None)))


class ForecastFrame(_ChecksTypes):
    def __init__(self, place: Optional[str] = None, date: Optional[datetime.date] = None,
                 daytime_id: Optional[int] = None, temperature_low: Optional[int] = None,
                 temperature_high: Optional[int] = None, feels_like: Optional[int] = None,
                 wind_speed: Union[int, float] = None, wind_direction: Optional[str] = None,
                 humidity_percentage: Union[int, str] = None, air_pressure: Optional[int] = None,
                 common_state: Optional[str] = None) -> None:
        """ common_state might be one of weather_forecast.common_states, like дождь or пасмурно """
        self.temperature_high = self.temperature_low = self.feels_like = self.wind_speed = None
        self.wind_direction = self.air_pressure = self.common_state = self.humidity_percentage = None
        self.date = self.place = self.daytime_id = None
        self.set_temperature(temp_low_high=(temperature_low, temperature_high))
        self.set_feels_like(feels_like=feels_like)
        self.set_wind_speed(wind_speed=wind_speed)
        self.set_wind_direction(wind_direction=wind_direction)
        self.set_humidity_percentage(humidity_percentage=humidity_percentage)
        self.set_air_pressure(air_pressure=air_pressure)
        self.set_common_state(common_state=common_state)
        self.set_place(place)
        self.set_date(date)
        self.set_daytime_id(daytime_id)

    def set_temperature(self, temp_low_high: Iterable[Optional[int]] = (None, None)) -> None:
        assert isinstance(temp_low_high, (list, tuple, set))
        assert len(temp_low_high) == 2
        if isinstance(temp_low_high[0], int) and isinstance(temp_low_high[1], int):
            assert temp_low_high[0] <= temp_low_high[1]
        self.set_temperature_low(temp_low_high[0])
        self.set_temperature_high(temp_low_high[1])

    def set_temperature_low(self, temperature_low: Optional[int] = None) -> None:
        _ChecksTypes.check_type_accept_none(temperature_low, int)
        self.temperature_low = temperature_low

    def set_temperature_high(self, temperature_high: Optional[int] = None) -> None:
        _ChecksTypes.check_type_accept_none(temperature_high, int)
        self.temperature_high = temperature_high

    def set_feels_like(self, feels_like: Optional[int] = None) -> None:
        _ChecksTypes.check_type_accept_none(feels_like, int)
        self.feels_like = feels_like

    def set_wind_speed(self, wind_speed: Optional[Union[int, float]] = None) -> None:
        _ChecksTypes.check_types_accept_none(wind_speed, (float, int))
        self.wind_speed = wind_speed

    def set_wind_direction(self, wind_direction: Optional[str] = None) -> None:
        _ChecksTypes.check_type_accept_none(wind_direction, str)
        # if wind_direction is not None and len(wind_direction) == 0:
        #     wind_direction = None
        self.wind_direction = wind_direction

    def set_humidity_percentage(self, humidity_percentage: Optional[Union[str, int]] = None) -> None:
        _ChecksTypes.check_types_accept_none(humidity_percentage, (int, str))
        if isinstance(humidity_percentage, str) and humidity_percentage[-1] == '%':
            humidity_percentage = int(humidity_percentage[:-1])
        if isinstance(humidity_percentage, int):
            assert 0 <= humidity_percentage <= 100
        self.humidity_percentage = humidity_percentage

    def set_air_pressure(self, air_pressure: Optional[int] = None) -> None:
        _ChecksTypes.check_type_accept_none(air_pressure, int)
        self.air_pressure = air_pressure

    def set_common_state(self, common_state: Optional[str] = None) -> None:
        _ChecksTypes.check_type_accept_none(common_state, str)
        if common_state is not None:
            common_state = common_state.lower()  # normalizing..
        assert common_state is None or common_state in common_states, 'Received unknown common state: ' + common_state
        self.common_state = common_state

    def is_ready_for_prediction(self) -> bool:
        date_present = isinstance(self.date, datetime.date)
        place_present = isinstance(self.place, str)
        daytime_id_present = isinstance(self.daytime_id, int) and is_valid_daytime_id(self.daytime_id)
        return date_present and place_present and daytime_id_present

    def as_pure_weather_info_dict(self) -> dict:
        pure_weather_keys = ['temperature_high', 'temperature_low', 'feels_like', 'wind_speed',
                             'air_pressure', 'humidity_percentage', 'common_state']
        return {key: value for key, value in self.__dict__.items() if key in pure_weather_keys}

    def stores_prediction(self):
        return self.is_ready_for_prediction() and list(self.as_pure_weather_info_dict().values()).count(None) < 4

    def set_date(self, date: Optional[datetime.date] = None) -> None:
        _ChecksTypes.check_type_accept_none(date, datetime.date)
        self.date = date

    def set_place(self, place: Optional[str] = None) -> None:
        _ChecksTypes.check_type_accept_none(place, str)
        self.place = place

    def set_daytime_id(self, daytime_id: Optional[int] = None) -> None:
        _ChecksTypes.check_type_accept_none(daytime_id, int)
        if daytime_id is not None:
            assert is_valid_daytime_id(daytime_id=daytime_id)
        self.daytime_id = daytime_id

    def to_string(self) -> str:
        """
        Returns its string representation, in order to be serialized
        :return: string representation
        """
        ret_dict = {key: value for key, value in self.__dict__.items()}
        ret_dict['date'] = ret_dict['date'].__repr__()
        return dumps(ret_dict)

    def from_string(self, string: str) -> None:
        """
        Loads its field from a passed string
        :param string: a string representation of object. Should be obtained with to_string method
        :return: None. The object itself gets updated
        """
        self.__dict__.update(loads(string))
        self.__dict__['date'] = eval(self.__dict__['date'])

    @staticmethod
    def create_from_string(string: str):
        """
        Returns a ForecastFrame object, recovered from the passed string
        :param string: a string from which the returning object gets initialized
        :return: recovered ForecastFrame object
        """
        forecast_frame = ForecastFrame()
        forecast_frame.from_string(string)
        return forecast_frame


class DayForecast(_ChecksTypes):
    def __init__(self, place: Optional[str] = None, date: Optional[datetime.date] = None,
                 morning_frame: Optional[ForecastFrame] = None, afternoon_frame: Optional[ForecastFrame] = None,
                 evening_frame: Optional[ForecastFrame] = None, night_frame: Optional[ForecastFrame] = None) -> None:
        self.date = self.place = None
        _ChecksTypes.check_type_accept_none(morning_frame, ForecastFrame)
        _ChecksTypes.check_type_accept_none(afternoon_frame, ForecastFrame)
        _ChecksTypes.check_type_accept_none(evening_frame, ForecastFrame)
        _ChecksTypes.check_type_accept_none(night_frame, ForecastFrame)

        self.frames = {DAYTIME_MORNING: morning_frame,
                       DAYTIME_AFTERNOON: afternoon_frame,
                       DAYTIME_EVENING: evening_frame,
                       DAYTIME_NIGHT: night_frame}

        for daytime_id in DAYTIME_IDS:
            if self[daytime_id] is None:
                self[daytime_id] = ForecastFrame(place=place, date=date, daytime_id=daytime_id)
        self.set_date(date=date)
        self.set_place(place=place)

    def set_date(self, date: Optional[datetime.date] = None) -> None:
        _ChecksTypes.check_type_accept_none(date, datetime.date)
        self.date = date
        for daytime_id in DAYTIME_IDS:
            if self[daytime_id] is not None:
                self[daytime_id].set_date(date)

    def set_place(self, place: Optional[str] = None) -> None:
        _ChecksTypes.check_type_accept_none(place, str)
        self.place = place
        for daytime_id in DAYTIME_IDS:
            if self[daytime_id] is not None:
                self[daytime_id].set_place(place)

    def is_ready_for_prediction(self) -> bool:
        ready = True
        for daytime_id in self:
            ready = ready and self[daytime_id].is_ready_for_prediction()
        return ready

    def stores_prediction(self) -> bool:
        stores = True
        for daytime_id in self:
            stores = stores and self[daytime_id].stores_prediction()
        return stores

    def as_pure_weather_info_dict(self, specify_daytime_id: Optional[int] = None) -> dict:
        assert is_valid_daytime_id(specify_daytime_id)
        if specify_daytime_id is None:
            specify_daytime_id = DAYTIME_AFTERNOON
        return self[specify_daytime_id].as_pure_weather_info_dict()

    def get_frame_by_daytime_name(self, daytime_name: str) -> ForecastFrame:
        assert daytime_name in DAYTIME_NAMES
        return self.frames[DAYTIME_NAMES.index(daytime_name)]

    def get_frame_by_datetime_name_en(self, daytime_name_en: str) -> ForecastFrame:
        assert daytime_name_en in DAYTIME_NAMES_EN
        return self.frames[DAYTIME_NAMES_EN.index(daytime_name_en)]

    def __getitem__(self, index: Union[str, int]) -> ForecastFrame:
        if isinstance(index, int):
            return self.frames[index]
        elif index in DAYTIME_NAMES:
            return self.get_frame_by_daytime_name(index)
        elif index in DAYTIME_NAMES_EN:
            return self.get_frame_by_datetime_name_en(index)
        else:
            assert False

    def __setitem__(self, index: Union[str, int], forecast_frame: ForecastFrame) -> None:
        assert isinstance(forecast_frame, ForecastFrame)
        if isinstance(index, int):
            self.frames[index] = forecast_frame
        elif index in DAYTIME_NAMES:
            daytime_name = index
            self.frames[DAYTIME_NAMES.index(daytime_name)] = forecast_frame
        elif index in DAYTIME_NAMES:
            daytime_name_en = index
            self.frames[DAYTIME_NAMES_EN.index(daytime_name_en)] = forecast_frame
        else:
            assert False

    def __iter__(self):
        return iter(DAYTIME_IDS)


class WeatherForecast(_ChecksTypes):
    def __init__(self, place: Optional[str] = None, dates: Optional[Iterable[datetime.date]] = None) -> None:
        self.place: str = None
        self.days_forecasts: Dict[datetime.date, DayForecast] = dict()

        _ChecksTypes.check_types_accept_none(dates, (list, tuple, set))
        if dates is None:
            dates = []

        for date in dates:
            self.add_day_forecast(DayForecast(place=place, date=date))
        self.set_place(place=place)

    def add_day_forecast(self, day_forecast: DayForecast) -> None:
        assert day_forecast.date not in self.days_forecasts
        self[day_forecast.date] = day_forecast

    def set_place(self, place: Optional[str] = None) -> None:
        _ChecksTypes.check_type_accept_none(place, str)
        self.place = place
        for day_forecast in self:
            day_forecast.set_place(place)

    def __getitem__(self, date: datetime.date) -> DayForecast:
        assert isinstance(date, datetime.date)
        return self.days_forecasts[date]

    def __setitem__(self, date: datetime.date, day_forecast: DayForecast) -> None:
        assert isinstance(day_forecast, DayForecast)
        assert self.place is None or self.place == day_forecast.place
        assert isinstance(date, datetime.date)
        assert day_forecast.date == date
        self.place = day_forecast.place
        self.days_forecasts[day_forecast.date] = day_forecast

    def __iter__(self):
        return iter(self.days_forecasts.values())

    def get_dates(self) -> List[datetime.date]:
        return list(self.days_forecasts.keys())

    def is_ready_for_prediction(self) -> bool:
        ready = True
        for day_forecast in self:
            ready = ready and day_forecast.is_ready_for_prediction()
            assert day_forecast.place == self.place
        ready = ready and isinstance(self.place, str)
        return ready

    def stores_prediction(self) -> bool:
        stores = True
        for day_forecast in self:
            stores = stores and day_forecast.stores_prediction()
            assert day_forecast.place == self.place
        return stores

    @staticmethod
    def unite_day_forecasts(day_forecasts: Optional[Iterable[DayForecast]] = None):
        """ accepts a list of DayForecast objects and unites it to the WeatherForecast """
        _ChecksTypes.check_types_accept_none(day_forecasts, (list, tuple, set))
        weather_forecast = WeatherForecast()
        if day_forecasts is None:
            day_forecasts = []
        for day_forecast in day_forecasts:
            weather_forecast.add_day_forecast(day_forecast)
        return weather_forecast

    @staticmethod
    def get_weather_forecast(place: str, dates: Iterable[datetime.date]):
        from modules.weather_forecast import fill_weather_forecast
        weather_forecast = WeatherForecast(place=place, dates=dates)
        weather_forecast = fill_weather_forecast(weather_forecast)
        return weather_forecast


def get_html_for_day_forecast(day_forecast: DayForecast) -> str:
    """
        returns html version of the weather forecast for one day,
        that is stored in the day_forecast (DayForecast type)
    """
    assert isinstance(day_forecast, DayForecast)

    date = day_forecast.date
    weekdays = '- понедельник вторник среда четверг пятница суббота воскресенье'.split()
    s = '<b>{2} - {0} - {1}</b>\n'.format(date.strftime('%d %b'), weekdays[date.isoweekday()].capitalize(), 
                                          day_forecast.place)
    months = {
        'January': 'января', 'Jan': 'января',
        'February': 'февраля', 'Feb': 'февраля',
        'March': 'марта', 'Mar': 'марта',
        'April': 'апреля', 'Apr': 'апреля',
        'May': 'мая',
        'June': 'июня', 'Jun': 'июня',
        'July': 'июля', 'Jul': 'июля',
        'August': 'августа', 'Aug': 'августа',
        'September': 'сентября', 'Sep': 'сентября',
        'October': 'октября', 'Oct': 'октября',
        'November': 'ноября', 'Nov': 'ноября',
        'December': 'декабря', 'Dec': 'декабря'
    }
    for m in months:
        s = s.replace(m, months[m])

    daytimes = ['утро', 'день', 'вечер', 'ночь']
    daytimes2 = ['Утром', 'Днем', 'Вечером', 'Ночью']
    s += '\n'
    
    for dt, dt2 in zip(daytimes, daytimes2):
        forecast_frame = day_forecast[dt]
        s += '<b>' + dt2.ljust(7) + '</b> будет {}, '.format(forecast_frame.common_state.lower())
        s += '<b>({0}..{1})</b>,\n'.format(forecast_frame.temperature_low, forecast_frame.temperature_high)

        if forecast_frame.feels_like:
            s += 'ощущается как <b>({})</b>\n'.format(forecast_frame.feels_like)

        if forecast_frame.wind_direction is not None and forecast_frame.wind_speed is not None:
            s += 'Ветер {0} - {1} м/с.\n'.format(forecast_frame.wind_direction, forecast_frame.wind_speed)
        else:
            s += 'Штиль\n'

        if forecast_frame.air_pressure is not None:
            s += 'Давление - {0} мм рт ст\n'.format(forecast_frame.air_pressure)
        
        if forecast_frame.humidity_percentage is not None:
            s += 'Влажность - {}%\n'.format(forecast_frame.humidity_percentage)
        s += '\n'
    return s


def get_htmls_for_weather_forecast(weather_forecast: WeatherForecast) -> List[str]:
    """ returns a list of htmls for the weather_forecast. Each element of that list is for one day. """
    return [get_html_for_day_forecast(day_forecast) for day_forecast in weather_forecast]
