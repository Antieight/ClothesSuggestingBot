import sys; sys.path.insert(0, '..')

from typing import List
from objects.clothes import ZONES

FEEDBACK_RANGE = list(range(-5, 6))
FeedbackType = int


def is_valid_feedback(feedback: FeedbackType) -> bool:
    return isinstance(feedback, FeedbackType) and feedback in FEEDBACK_RANGE


ZoneFeedbackType = List[int]


def is_valid_zone_feedback(zone_feedback: ZoneFeedbackType) -> bool:
    valid = isinstance(zone_feedback, (list, tuple, set))
    valid = valid and len(zone_feedback) == len(ZONES)
    for feedback in zone_feedback:
        valid = valid and is_valid_feedback(feedback)
    return valid
