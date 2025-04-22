def clamp(low: float, val: float, hi: float) -> float:
    """Clamp `val` between `low` and `hi`"""
    return max(min(val, hi), low)


def red_scale(value: float) -> str:
    """Interpolate between red and green background colour"""
    low = 183
    high = 255
    diff = value * (high - low)
    r = round(clamp(0, high - diff, 255))
    g = round(clamp(0, low + diff, 255))
    # Blue value takes lowest value if it is lower than default low value
    b = min(r, g, low)

    color = f"rgb({r}, {g}, {b})"
    return color
