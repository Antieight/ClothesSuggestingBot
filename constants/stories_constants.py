STORY_WEATHER_FORECAST_REQUEST = 0
STORY_SUBSCRIPTION_MANAGEMENT = 1
STORY_WARDROBE_MANAGEMENT = 2
STORY_CLOTHES_SET_REQUEST = 3
STORY_FEEDBACK = 4
STORY_NO_STORY = None


def is_valid_story_id(story_id: int) -> bool:
    return story_id in range(5) or story_id is None
