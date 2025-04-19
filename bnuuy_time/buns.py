from datetime import datetime
import json
import random
from typing import NotRequired, TypedDict


class BunSource(TypedDict):
    """Credit the bun's hoom"""

    platform: str
    """Platform where image is from (eg 'Reddit')"""
    author: str
    """Author's username"""
    url: str
    """URL of post where bun was shared"""


class BunDefinition(TypedDict):
    filename: str
    """filename in src/static/buns/"""
    name: str | None
    """name of bun, or None if name not known"""
    source: BunSource
    """Credit to bun's hoom"""
    left_ear: int
    """Left ear time, as hour"""
    right_ear: int
    """Right ear time, as hour"""
    focus_x: NotRequired[float]
    """Focus point within 0-1 on x-axis. Defaults to 0.5"""
    focus_y: NotRequired[float]
    """Focus point within 0-1 on y-axis. Defaults to 0.5"""


DEFAULT_FOCUS = 0.5
"""Default focal point of bun photo"""


BUNS_FILE = "buns.json"


def load_buns() -> list[BunDefinition]:
    with open(BUNS_FILE) as f:
        return json.load(f)


def bun_matches(time: datetime, bun: BunDefinition) -> bool:
    """
    Returns whether this bun matches the given time
    """
    hour_oclock = time.hour % 12
    if hour_oclock == 0:
        hour_oclock = 12
    minute_oclock = round(time.minute / 5)
    if minute_oclock == 0:
        minute_oclock = 12

    left_ear = bun["left_ear"]
    right_ear = bun["right_ear"]

    # Left ear is hour hand, right ear is minute hand
    if hour_oclock == left_ear and minute_oclock == right_ear:
        return True
    # Left ear is minute hand, right ear is hour hand
    elif hour_oclock == right_ear and minute_oclock == left_ear:
        return True
    else:
        return False


def find_matching_bun(time: datetime) -> BunDefinition | None:
    """
    Find a bun that matches the given time. If there are multiple possible
    buns, pick one randomly.
    """
    buns = load_buns()
    matches = [bun for bun in buns if bun_matches(time, bun)]
    if len(matches) == 0:
        return None
    return random.choice(matches)


def hour_to_random_minute(hour: int) -> int:
    """
    Given an hour-hand value, return a reasonable minute-hand value.
    """
    if hour == 12:
        return random.choice([58, 59, 0, 1, 2])
    centre_point = hour * 5
    return random.choice(range(centre_point - 2, centre_point + 3))


def generate_time_for_bun(bun: BunDefinition) -> datetime:
    """
    Generate a random time that this bun says it is.
    """
    # Decide which ear is hour and which is minute
    if random.randint(0, 1):
        # Left ear is hour hand
        hour = bun["left_ear"]
        minute = hour_to_random_minute(bun["right_ear"])
    else:
        # Right ear is hour hand
        hour = bun["right_ear"]
        minute = hour_to_random_minute(bun["left_ear"])
    # AM or PM
    if random.randint(0, 1):
        hour = (hour + 12) % 24

    return datetime.now().replace(hour=hour, minute=minute)


def find_bun_with_filename(filename: str) -> BunDefinition | None:
    """
    Find a bun whose image file matches
    """
    buns = load_buns()
    for bun in buns:
        if bun["filename"] == filename:
            return bun
    return None
