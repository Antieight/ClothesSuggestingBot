import sys; sys.path.insert(0, '..')

from objects.clothes import *
from objects.weather_forecast import *
from objects.history_table import *
import pandas as pd
from typing import List

"""
This file represents the interface we need to implement for the bot to be able to offer some clothes sets
"""
def generate_User_degree_table(user_id: str):
    updated_degree_table = pd.read_csv('data\default_degree_table.csv')
    uht = UserHistoryTable(user_id)
    s = uht.get_dataframe_representation()
    s.iloc[0:1, 0] = 3
    s.iloc[0:1, -5:] = 1
    list_of_columns = list(s.columns)
    list_of_clothes = list_of_columns[:updated_degree_table.shape[1]]
    list_of_zones = list_of_columns[len(list_of_columns) - 5:]

    for i in range(0, len(list_of_zones)):
        a = list_of_zones[i]
        list_of_zones[i] = a[len('score_'):]

    for i in range(0, len(list_of_clothes)):
        a = list_of_clothes[i]
        list_of_clothes[i] = a[len('clothes_item_')+1:]


    for i in range(0,s.shape[0]):
        print('i=',i)
        for j in range(0,len(list_of_zones)):
            print('i=', i, 'j=',j)
            if s.iloc[i,len(list_of_columns)-j-1] != 0:
                for k in range(0,len(list_of_clothes)):
                    #print('i=', i, 'j=', j,'k=',k)
                    #print('Значение =', s.iloc[i,k])
                    #print('Пусто? ', s.iloc[i,k])
                    #print('Вещь =', list_of_clothes[k])
                    #print('ID вещи =', get_clothing_item_id(list_of_clothes[k]))
                    #print('Зона вещи =', get_zone_id(get_clothing_item_id(list_of_clothes[k])))
                    #print('ID зоны =', list_of_zones[j], 'а надо =', ZONES_NAMES_RU.index(list_of_zones[j]))
                    if (s.iloc[i,k] != 0) and (get_zone_id(get_clothing_item_id(list_of_clothes[k])) == ZONES_NAMES_RU.index(list_of_zones[j])):
                        print('есть update','i=',i,'j=',j,'k=',k)
                        delta = s.iloc[i,k] - s.iloc[i,len(list_of_columns)-j-1]
                        print(delta)
                        a = updated_degree_table.iloc[0,k]
                        updated_degree_table.iloc[0,k] = a + delta

    return updated_degree_table


def get_score(clothes_set: ClothesSet, forecast_frame: ForecastFrame, user_id: str) -> int:
    """
    Returns the score for the given clothes set, when the weather as in the forecast frame.
    :param clothes_set: the ClothesSet stores the set of clothes
    :param forecast_frame: the forecast_frame stores the weather_forecast for some daytime of date at some place
    :param user_id: by user_id one can get his HistoryTable
    :return: the score from -5 to 5, -5 -- very cold clothes_set, 5 -- too warm clothes_set
    """

    def func_delta(x):
        y = 30.46 - 10.41 * x
        return y

    def temperature_to_degree(clothes_set: ClothesSet, forecast_frame: ForecastFrame):
        delta_heads = round(forecast_frame.feels_like - (func_delta(cl.degree[0][i_1])), 2)
        delta_torsos = round(forecast_frame.feels_like - (func_delta(cl.degree[1][i_2])), 2)
        delta_legs = round(forecast_frame.feels_like - (func_delta(cl.degree[2][i_3])), 2)
        delta_feet = round(forecast_frame.feels_like - (func_delta(cl.degree[3][i_4])), 2)
        delta_hands = round(forecast_frame.feels_like - (func_delta(cl.degree[4][i_5])), 2)

        delta_list = [delta_heads, delta_torsos, delta_legs, delta_feet, delta_hands]
        return delta_list


    return 0



def generate_clothes_set(forecast_frame: ForecastFrame, user_id: str) -> ClothesSet:
    """
    Generates the clothes_set, that will suit the weather forecast the most.
    Users preferences should be taken into account as well.
    His history may be found and grabbed with UserHistoryTable(user_id=user_id)
    :param forecast_frame: the weather forecast
    :param user_id: the user_id
    :return: the offered clothes_set
    """
    return ClothesSet(['кепка', 'кеды', 'футболка'])


def regenerate_zone(zone_id_to_regenerate: int, forecast_frame: ForecastFrame,
                    clothes_set_current_offering: ClothesSet, user_id: str) -> ClothesSet:
    """
    Regenerates the specified zone for the user
    :param zone_id_to_regenerate: which zone to regenerate
    :param forecast_frame: weather forecast
    :param clothes_set_current_offering: current ClothesSet object, we already generated for him
    :param user_id: user_id
    :return: The refreshed ClothesSet
    """
    clothes_set_current_offering[zone_id_to_regenerate * 1000] += 1
    clothes_set_current_offering[zone_id_to_regenerate * 1000] %= 5
    return clothes_set_current_offering
