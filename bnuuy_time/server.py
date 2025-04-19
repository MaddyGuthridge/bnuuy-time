from datetime import datetime
import random
from zoneinfo import ZoneInfo
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


def bnuuy_time(bun: BunDefinition, time: datetime):
    t = format_time(time)

    name = bun["name"]
    if name is None:
        name = random.choice(["Bun", "Bunny", "Bnuuy"])

    # Credits
    source = bun["source"]
    credits = p.a(href=source["url"], target="_blank")(
        f"{source['author']} on {source['platform']}",
    )

    # Focus point
    focus_x = bun.get("focus_x", DEFAULT_FOCUS)
    focus_y = bun.get("focus_y", DEFAULT_FOCUS)

    return str(
        p.html(
            p.head(
                p.link(rel="stylesheet", href="/static/style.css"),
            ),
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
                        p.span(class_="shadow")(credits),
                    ),
                ),
            ),
        )
    )


@app.get("/")
def redirect_with_tz():
    return redirect("/Australia/Sydney")


@app.get("/buns/<bun_file>")
def with_bun(bun_file: str):
    bun = find_bun_with_filename(bun_file)

    if bun is None:
        return f"No buns with filename {bun_file}"
    else:
        return bnuuy_time(bun, generate_time_for_bun(bun))


@app.get("/<time_str>")
def at_time(time_str: str):
    parsed = parse_time(time_str)

    if parsed is None:
        print("Unable to parse time")
        return "Unable to parse time"
    else:
        bun = find_matching_bun(parsed)
        if bun is None:
            return f"No matching buns at {parsed} :("
        return bnuuy_time(bun, parsed)


@app.get("/<region>/<location>")
def from_region(region: str, location: str):
    now = now_in_tz(ZoneInfo(f"{region}/{location}"))
    bun = find_matching_bun(now)
    if bun is None:
        return f"No matching buns at {now} :("
    return bnuuy_time(bun, now)


if __name__ == "__main__":
    app.run()
