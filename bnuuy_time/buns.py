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
    source: BunSource | None
    """Credit to bun's hoom"""
    left_ear: int
    """Left ear time, in degrees"""
    right_ear: int
    """Right ear time, in degrees"""
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


def bun_closeness(time: datetime, bun: BunDefinition) -> int:
    """
    Returns the total number of degrees between this bun's ears and the hands
    of the clock.
    """
    minute_degrees = time.minute * 5
    # Includes the minute hand's effect on the hour hand
    hour_degrees = round(time.hour % 12 * 30 + minute_degrees / 12) % 360

    left_ear = bun["left_ear"]
    right_ear = bun["right_ear"]

    # Consider both the left and right ears as the hour hand
    left_hour = abs(hour_degrees - left_ear) + abs(minute_degrees - right_ear)
    right_hour = abs(hour_degrees - right_ear) + abs(minute_degrees - left_ear)

    # Pick whichever is closest
    return min(left_hour, right_hour)


def find_matching_bun(time: datetime) -> BunDefinition | None:
    """
    Find a bun that matches the given time. If there are multiple possible
    buns, pick one randomly.
    """
    # Max number of degrees of difference between the bun and the hour hands
    MAX_THRESHOLD = 30
    # Buns that are within this many degrees of the lowest value are also valid
    ALSO_VALID_THRESHOLD = 10

    buns = load_buns()

    # Current matches
    matches: list[BunDefinition] = []
    # Total number of degrees between the closest match and the actual time
    closest_distance = MAX_THRESHOLD

    for bun in buns:
        closeness = bun_closeness(time, bun)
        if closeness > MAX_THRESHOLD:
            continue
        elif closeness < closest_distance:
            # This bun is a new best distance
            matches.append(bun)
            # Filter matches based on the new closeness
            # They must have a closeness less than `closeness + ALSO_VALID_THRESHOLD`
            matches = [
                match
                for match in matches
                if bun_closeness(time, match) <= closeness + ALSO_VALID_THRESHOLD
            ]
            closest_distance = closeness
        elif closeness <= closest_distance + ALSO_VALID_THRESHOLD:
            # Bun is close enough, but isn't a new best distance
            matches.append(bun)
        else:
            # Bun is not close enough
            continue

    # No matches were close enough to consider valid
    if len(matches) == 0:
        return None
    # Choose one of the best options randomly
    return random.choice(matches)


def generate_time_for_bun(bun: BunDefinition) -> datetime:
    """
    Generate a random time that this bun says it is.
    """
    # Decide which ear is hour and which is minute
    if random.randint(0, 1):
        # Left ear is hour hand
        hour = bun["left_ear"] // 30
        minute = bun["right_ear"] // 6
    else:
        # Right ear is hour hand
        hour = bun["right_ear"] // 30
        minute = bun["left_ear"] // 6
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
