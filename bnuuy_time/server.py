from datetime import datetime
import random
from zoneinfo import ZoneInfo
from flask import Flask, redirect
import pyhtml as p

from bnuuy_time.buns import find_matching_bun

from .times import format_time, now_in_tz, parse_time


app = Flask(__name__)


def bnuuy_time(time: datetime):
    t = format_time(time)

    bun = find_matching_bun(time)

    if bun is None:
        return f"No matching buns at {t} :("

    name = bun["name"]
    if name is None:
        name = random.choice(["Bun", "Bunny", "Bnuuy"])

    # Credits
    source = bun["source"]
    credits = p.a(href=source["url"], target="_blank")(
        f"{source['author']} on {source['platform']}",
    )

    return str(
        p.html(
            p.head(
                p.link(rel="stylesheet", href="/static/style.css"),
            ),
            p.body(
                p.img(
                    id="bun-img",
                    src=f"/static/buns/{bun['filename']}",
                    alt=f"{name}'s ears are telling the time like an analog clock, and say that the time is {t}",
                ),
                p.div(class_="center")(
                    p.main(
                        p.h1(f"{name} says that it is {t}"),
                        credits,
                    ),
                ),
            ),
        )
    )


@app.get("/")
def redirect_with_tz():
    return redirect("/Australia/Sydney")


@app.get("/<time_str>")
def at_time(time_str: str):
    parsed = parse_time(time_str)

    if parsed is None:
        print("Unable to parse time")
        return "Unable to parse time"
    else:
        return bnuuy_time(parsed)


@app.get("/<region>/<location>")
def from_region(region: str, location: str):
    now = now_in_tz(ZoneInfo(f"{region}/{location}"))
    return bnuuy_time(now)


if __name__ == "__main__":
    app.run()
