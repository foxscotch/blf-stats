import json
import requests
from bs4 import BeautifulSoup


class Period:
    year: int
    month: int

    def __init__(self, year: int, month: int):
        self.year = year
        self.month = month


DATA_FILE_PATH = "./data.json"

BASE_URL = "https://forum.blockland.us/index.php"

# actual xml param should merely be present but idk how tf to do that with requests and 1 works sooo
BASE_PARAMS = { 'action': 'stats', 'xml': '1' }

EARLIEST_PERIOD = (2009, 8)


def month_params(period: Period):
    #                                             v  i mean, like, we're not actually going to be encountering any dates earlier than 1000 BC. but like what if
    return BASE_PARAMS | { 'expand': f"{period.year:0>2}{period.month:0>2}" }


def get_days(raw_xml: str):
    soup = BeautifulSoup(raw_xml, 'xml')

def get_month_data(period: Period):
    pass

def get_year_data(period: Period):
    pass

def get_daily_statistics(data: dict):
    pass


def load_data():
    try:
        with open(DATA_FILE_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data: dict):
    with open(DATA_FILE_PATH, 'w') as f:
        json.dump(data, f)


def main():
    # this is where we store alllllll the data; loaded from a file at the start, saved to it at the end
    data = load_data()

    get_daily_statistics(data)

    save_data(data)


if __name__ == '__main__':
    main()
