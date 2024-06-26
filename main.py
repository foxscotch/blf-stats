import json
import itertools
import time
from dataclasses import dataclass
from datetime import datetime
from collections.abc import Iterable

import requests
from bs4 import BeautifulSoup


@dataclass
class Period:
    """represents a year and month, which is the most granular period of data available. and also the only period"""

    year: int
    month: int

    @classmethod
    def from_string(cls, string):
        return cls(int(string[:4]), int(string[5:]))

    def __repr__(self):
        return f"{self.year}-{self.month}"


DATA_FILE_PATH = "./data.json"
"""where we'll store data and later load it from"""

BASE_URL = "https://forum.blockland.us/index.php"

# actual xml param should merely be present but idk how tf to do that with requests and 1 works sooo
BASE_PARAMS = {"action": "stats", "xml": "1"}

EARLIEST_PERIOD = Period(2009, 8)
"""earliest period for which there is data available"""


def find_max_period(stats) -> tuple[str, int]:
    """find the latest period and its index at the same time"""

    max_period = "000000"
    encountered = 0

    for i, day in enumerate(stats):
        period = day["date"][:7].replace("-", "")
        if period > max_period:
            encountered = i
            max_period = period

    return max_period, encountered


def month_params(period: Period) -> dict[str, str]:
    """generate request params for a given period"""
    return BASE_PARAMS | {"expand": f"{period.year:0>2}{period.month:0>2}"}


def get_period_data(period: Period) -> Iterable[dict[str, str]]:
    """get all of the data for a given period"""

    now = datetime.now().isoformat()
    response = requests.get(BASE_URL, month_params(period))
    soup = BeautifulSoup(response.text, "xml")

    print(f"Fetched data for {period}")

    for day in soup.find_all("day"):
        yield {
            "date": day["date"],
            "new_topics": day["new_topics"],
            "new_posts": day["new_posts"],
            "new_members": day["new_members"],
            "most_members_online": day["most_members_online"],
            "hits": day["hits"],
            "collected_at": now,
        }


def get_daily_statistics(existing_data: dict):
    """retrieve all daily statistics"""

    stats: list[str, any] = existing_data.get("daily_statistics", [])
    start_period = EARLIEST_PERIOD

    if "daily_statistics" in existing_data:
        max_date, max_date_index = find_max_period(stats)
        del stats[max_date_index:]
        start_period = Period.from_string(max_date)

    try:
        for year in itertools.count(start_period.year):
            start_month = start_period.month if year == start_period.year else 1
            for month in range(start_month, 13):
                stats.extend(get_period_data(Period(year, month)))
                time.sleep(0.5)  # don't want to make too many requests too fast
    except KeyboardInterrupt:
        pass  # if interrupted, just return what we've got so far

    return sorted(stats, key=lambda d: d["date"])


def load_data():
    try:
        with open(DATA_FILE_PATH, "r") as f:
            print(f"Loading from {DATA_FILE_PATH}")
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_data(data: dict):
    with open(DATA_FILE_PATH, "w") as f:
        json.dump(data, f, indent=2)
        print(f"Saved to {DATA_FILE_PATH}")


def main():
    # this is where we store alllllll the data; loaded from a file at the start, saved to it at the end
    data = load_data()

    data["daily_statistics"] = get_daily_statistics(data)

    save_data(data)


if __name__ == "__main__":
    main()
