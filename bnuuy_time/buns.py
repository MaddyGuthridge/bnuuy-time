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
    name: str | list[str] | None
    """name of bun, list of potential names, or None if name not known"""
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



MAX_THRESHOLD = 90
"""
Max number of degrees of difference between the bun and the hour hands.
This value is pretty high, so some buns will be inaccurate sometimes.
At least the ALSO_VALID_THRESHOLD should prevent inaccurate values unless
there is no alternative.
"""

ALSO_VALID_THRESHOLD = 20
"""
Buns that are within this many degrees of the lowest value are also valid.
"""

BUNS_FILE = "buns.json"


def load_buns() -> list[BunDefinition]:
    with open(BUNS_FILE) as f:
        return json.load(f)


def angle_diff(a: int, b: int) -> int:
    """
    Difference between angles, accounting for wrap-around at 360 degrees
    """
    return min(abs(a - b), 360 - abs(a - b))


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
    left_hour = angle_diff(hour_degrees, left_ear) + angle_diff(
        minute_degrees, right_ear
    )
    right_hour = angle_diff(hour_degrees, right_ear) + angle_diff(
        minute_degrees, left_ear
    )

    # Pick whichever is closest
    return min(left_hour, right_hour)


def find_matching_buns(time: datetime) -> list[tuple[int, BunDefinition]]:
    """
    Return all matching buns at the given time.

    Returns matching buns as a tuple of `(closeness, bun)`, where buns with a
    lower closeness value are closest to the preferred times.
    """

    buns = load_buns()

    # Current matches, in the form `(closeness, bun)`
    matches: list[tuple[int, BunDefinition]] = []
    # Total number of degrees between the closest match and the actual time
    closest_distance = MAX_THRESHOLD

    for bun in buns:
        closeness = bun_closeness(time, bun)
        if closeness > MAX_THRESHOLD:
            # Bun is too far away to even consider it
            continue
        elif closeness < closest_distance:
            # This bun is a new best distance
            matches.append((closeness, bun))
            # Filter matches based on the new closeness
            # They must have a closeness less than `closeness + ALSO_VALID_THRESHOLD`
            matches = [
                (c, match)
                for c, match in matches
                if c <= closeness + ALSO_VALID_THRESHOLD
            ]
            closest_distance = closeness
        elif closeness <= closest_distance + ALSO_VALID_THRESHOLD:
            # Bun is close enough, but isn't a new best distance
            matches.append((closeness, bun))
        else:
            # Bun is not close enough
            continue

    return matches


def find_matching_bun(time: datetime) -> BunDefinition | None:
    """
    Find a bun that matches the given time. If there are multiple possible
    buns, pick one randomly.
    """
    matches = find_matching_buns(time)

    # No matches were close enough to consider valid
    if len(matches) == 0:
        return None

    closest_distance = min(m[0] for m in matches)

    # Choose one of the best options weighting them so that closer buns are
    # more likely
    # Rewrite the value so that closest bun has a weighting of 10, and other
    # buns have weighting based on how close they are to the closest
    matches = [(MAX_THRESHOLD - (c - closest_distance), bun) for c, bun in matches]
    # Unzip iterator using zip(*matches), and convert the results to a list
    # https://book.pythontips.com/en/latest/zip.html
    weights, matched_buns = map(list, zip(*matches))
    return random.choices(matched_buns, weights)[0]


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
