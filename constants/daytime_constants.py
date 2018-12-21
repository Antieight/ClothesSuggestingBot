DAYTIME_MORNING = 0
DAYTIME_AFTERNOON = 1
DAYTIME_EVENING = 2
DAYTIME_NIGHT = 3

DAYTIME_NAMES = ['утро', 'день', 'вечер', 'ночь']
DAYTIME_NAMES_EN = ['morning', 'afternoon', 'evening', 'night']
DAYTIME_IDS = [DAYTIME_MORNING, DAYTIME_AFTERNOON, DAYTIME_EVENING, DAYTIME_NIGHT]


def is_valid_daytime_id(daytime_id: int) -> bool:
    return daytime_id in range(4)
