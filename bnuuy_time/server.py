from datetime import datetime
import random
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from flask import Flask, redirect
import pyhtml as p

from .buns import (
    DEFAULT_FOCUS,
    BunDefinition,
    find_bun_with_filename,
    find_matching_bun,
    generate_time_for_bun,
)

from .times import format_time, now_in_tz, parse_time


app = Flask(__name__)


def generate_head(
    title: str | None,
    extra_css: list[str],
):
    title = f"{title} - Bnuuy Time" if title else "Bnuuy time"
    return p.head(
        p.title(title),
        [p.link(rel="stylesheet", href=css_file) for css_file in extra_css],
        p.meta(
            name="description",
            content="When you visit this webpage, a bunny rabbit will tell you what time it is",
        ),
        p.meta(name="keywords", content="clock, time, bunny, rabbit, Maddy Guthridge"),
        p.meta(name="author", content="Maddy Guthridge"),
        p.meta(name="viewport", content="width=device-width, initial-scale=1.0"),
    )


def bnuuy_time(bun: BunDefinition, time: datetime):
    t = format_time(time)

    name = bun["name"]
    if name is None:
        name = random.choice(["Bun", "Bunny", "Bnuuy"])

    # Credits
    source = bun["source"]
    if source is not None:
        credits = p.a(href=source["url"], target="_blank")(
            f"{source['author']} on {source['platform']}",
        )
    else:
        credits = None

    # Focus point
    focus_x = bun.get("focus_x", DEFAULT_FOCUS)
    focus_y = bun.get("focus_y", DEFAULT_FOCUS)

    return str(
        p.html(
            generate_head(t, ["/static/style.css"]),
            p.body(
                p.div(class_="background-container")(
                    p.img(
                        id="bun-img",
                        style=f"--crop-focus-x: {focus_x}; --crop-focus-y: {focus_y}",
                        src=f"/static/buns/{bun['filename']}",
                        alt=f"{name}'s ears are telling the time like an analog clock, and say that the time is {t}",
                    ),
                ),
                p.div(class_="center")(
                    p.main(
                        p.h1(class_="shadow")(
                            f"{name} says that it is",
                            p.span(class_="no-wrap")(t),
                        ),
                        p.span(class_="shadow")("Credit: ", credits) if credits else [],
                    ),
                ),
            ),
        )
    )


def error_page(reason: str):
    return str(
        p.html(
            generate_head("Error", []),
            p.body(
                p.h1("No matching bunnies"),
                p.p(reason),
                p.p("I'll add more bunnies over time..."),
            ),
        )
    )


@app.get("/")
def redirect_with_tz():
    return str(
        p.html(
            generate_head(None, []),
            p.body(
                p.h1("Bnuuy time"),
                p.p("Redirecting to your time zone..."),
                p.script(src="/static/tz_redirect.js"),
            ),
        )
    )


@app.get("/coverage")
def coverage():
    start_hour = 1
    start_minute = 0
    covered = True
    coverage_times = []
    minutes_covered = 0
    minutes_uncovered = 0
    for hour in range(1, 13):
        for minute in range(60):
            t = datetime.now().replace(hour=hour, minute=minute)
            found_bun = find_matching_bun(t) is not None
            if found_bun and not covered:
                # Only add if it is a reasonable span of time
                coverage_times.append(
                    p.tr(_class="not-covered")(
                        p.td(f"{start_hour}:{start_minute:02} - {hour}:{minute:02}"),
                        p.td("No"),
                    )
                )
                covered = True
                start_hour = hour
                start_minute = minute
            elif not found_bun and covered:
                covered = False
                coverage_times.append(
                    p.tr(_class="covered")(
                        p.td(f"{start_hour}:{start_minute:02} - {hour}:{minute:02}"),
                        p.td("Yes"),
                    )
                )
                start_hour = hour
                start_minute = minute
            if covered:
                minutes_covered += 1
            else:
                minutes_uncovered += 1

    # Add final time span
    coverage_times.append(
        p.tr(_class="covered" if covered else "not-covered")(
            p.td(f"{start_hour:02}:{start_minute:02} - 12:59"),
            p.td("Yes" if covered else "No"),
        )
    )

    total_minutes = minutes_covered + minutes_uncovered
    percent_covered = minutes_covered / total_minutes * 100

    return str(
        p.html(
            generate_head("Bun coverage", ["/static/coverage.css"]),
            p.body(
                p.h1("Bun coverage"),
                p.p(
                    f"{minutes_covered} / {total_minutes} minutes covered ({percent_covered:.0f}%)"
                ),
                p.table(
                    p.thead(
                        p.tr(
                            p.th("Time span"),
                            p.th("Covered?"),
                        ),
                    ),
                    p.tbody(
                        coverage_times,
                    ),
                ),
            ),
        )
    )


@app.get("/buns/<path:bun_file>")
def with_bun(bun_file: str):
    bun = find_bun_with_filename(bun_file)

    if bun is None:
        return error_page(f"No buns with filename {bun_file}")
    else:
        return bnuuy_time(bun, generate_time_for_bun(bun))


@app.get("/<time_str>")
def at_time(time_str: str):
    # Convenience redirects for common time zones
    abbreviation_redirects = {
        "UTC": "Etc/UTC",
        "GMT": "Europe/London",
    }
    if time_str in abbreviation_redirects:
        return redirect(f"{abbreviation_redirects[time_str]}")

    parsed = parse_time(time_str)

    if parsed is None:
        return error_page(f"Unable to parse the time string '{time_str}'")
    else:
        bun = find_matching_bun(parsed)
        if bun is None:
            return str(error_page(f"No matching buns at {format_time(parsed)} :("))
        return bnuuy_time(bun, parsed)


@app.get("/<region>/<location>")
def from_region(region: str, location: str):
    try:
        now = now_in_tz(ZoneInfo(f"{region}/{location}"))
    except ZoneInfoNotFoundError:
        return error_page(f"The time zone '{region}/{location}' does not exist")
    bun = find_matching_bun(now)
    if bun is None:
        return error_page(f"No matching buns at {format_time(now)} :(")
    return bnuuy_time(bun, now)


if __name__ == "__main__":
    app.run()
