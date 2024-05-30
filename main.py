import json
import itertools
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
        cls(int(string[:4]), int(string[5:]))


DATA_FILE_PATH = "./data.json"

BASE_URL = "https://forum.blockland.us/index.php"

# actual xml param should merely be present but idk how tf to do that with requests and 1 works sooo
BASE_PARAMS = {"action": "stats", "xml": "1"}

EARLIEST_PERIOD = Period(2009, 8)


def find_max_period(stats) -> tuple[str, int]:
    """find the latest period and its index at the same time"""

    max_period = "000000"
    encountered = 0

    for i, day in enumerate(stats):
        period = day["date"][:7].replace("-", "")
        if period > max_period:
            encountered = i
            max_period = period

    return (max_period, encountered)


def month_params(period: Period) -> dict[str, str]:
    """generate request params for a given period"""

    #                                              v  i mean, like, we're not actually going to be encountering any dates earlier than 1000 BC. but like what if
    return BASE_PARAMS | {"expand": f"{period.year:0>2}{period.month:0>2}"}


def get_period_data(period: Period) -> Iterable[dict[str, str]]:
    """get all of the data for a given period"""

    now = datetime.now().isoformat()
    response = requests.get(BASE_URL, month_params(period))
    soup = BeautifulSoup(response.text, "xml")

    for day in soup.find_all("days"):
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

    stats: list[str, any] = existing_data["daily_statistics"]
    start_period = EARLIEST_PERIOD

    if "daily_statistics" in existing_data:
        max_date, max_date_index = find_max_period(stats)
        del stats[max_date_index:]
        start_period = Period.from_string(max_date)

    for year in itertools.count(start_period.year):
        start_month = start_period.month if year == start_period.year else 1
        for month in range(start_month, 13):
            stats.extend(get_period_data(Period(year, month)))

    return stats.sort()


def load_data():
    try:
        with open(DATA_FILE_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_data(data: dict):
    with open(DATA_FILE_PATH, "w") as f:
        json.dump(data, f)


def main():
    # this is where we store alllllll the data; loaded from a file at the start, saved to it at the end
    data = load_data()

    get_daily_statistics(data)

    save_data(data)


if __name__ == "__main__":
    main()
