from datetime import datetime, tzinfo


def format_time(time: datetime):
    return time.strftime("%-I:%M %p")


def parse_time(time_str: str) -> datetime | None:
    # Try various formats
    formats = [
        "%H:%M",
        "%I:%M %p",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(time_str, fmt)
        except Exception as e:
            print(e)
    return None


def now_in_tz(tz: tzinfo):
    return datetime.now(tz)
