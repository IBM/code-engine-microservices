from app.errors import illegal_date, item_not_found
import os
import json
import copy
from datetime import datetime, timedelta

HOTELS_PATH = os.path.join(os.getcwd(), "data/hotel-data.json")
HOTEL_INFO_PATH = os.path.join(os.getcwd(), "data/hotel-info.json")

# Cities with these words in the city name are lower case
lc_exceptions = ["es", "de", "au"]

hotel_data = None
hotel_info = None


def capitalize(text):
    split_text = text.lower().split("-")
    text = list(map(lambda s: s if s in lc_exceptions else s.capitalize(), split_text))

    # The city of Port-au-Prince keeps "-" between the words of the city
    return "-".join(text) if lc_exceptions[2] in text else " ".join(text)


def parse_metadata(file):
    with open(file, "r") as f:
        content = f.read()
    metadata = json.loads(content)
    return metadata


def get_hotel_data():
    global hotel_data
    if hotel_data is None:
        hotel_data = parse_metadata(HOTELS_PATH)
    return hotel_data


def get_hotel_info():
    global hotel_info
    if hotel_info is None:
        hotel_info = parse_metadata(HOTEL_INFO_PATH)
    return hotel_info


def get_hotels(country, city, filters, context):
    if filters["date_to"] - filters["date_from"] < timedelta(0):
        raise illegal_date.IllegalDateException(
            "from date can not be greater than to date"
        )

    context.start("getHotelDataFromLocal")
    metadata = copy.deepcopy(get_hotel_data())
    context.stop()

    hotels_data = list(
        filter(lambda h: filter_city_hotels(h, country, city, filters), metadata)
    )

    return update_cost(hotels_data, filters["date_from"])


def get_filter_list(filter_type, context):
    context.start("getHotelInfoFromLocal")
    metadata = get_hotel_info()
    context.stop()
    return list(set([item[filter_type] for item in metadata]))


def get_hotel_by_id(id, filters, context):
    if filters["date_to"] - filters["date_from"] < timedelta(0):
        raise illegal_date.IllegalDateException(
            "from date can not be greater than to date"
        )

    context.start("getHotelDataFromLocal")
    data = get_hotel_data()
    context.stop()

    try:
        res = list(filter(lambda item: item["id"] == id, data))[0]
    except IndexError:
        raise item_not_found.ItemNotFoundException(id)

    multiplier = date_multiplier(filters["date_from"])
    res["cost"] = res["cost"] * multiplier
    res["dateFrom"] = filters["date_from"].strftime("%Y-%m-%d")
    res["dateTo"] = filters["date_to"].strftime("%Y-%m-%d")
    return res


def readiness_check():
    return True


def update_cost(data, date):
    multiplier = date_multiplier(date)

    for hotel in data:
        hotel["cost"] = hotel["cost"] * multiplier

    return data


def date_multiplier(date_from):
    date_now = datetime.now()
    num_days = (date_from - date_now).days
    if num_days < 0:
        raise illegal_date.IllegalDateException(date_from)
    elif num_days < 2:
        return 2.25
    elif num_days < 7:
        return 1.75
    elif num_days < 14:
        return 1.5
    elif num_days < 21:
        return 1.2
    elif num_days < 45:
        return 1
    elif num_days < 90:
        return 0.8
    else:
        raise illegal_date.IllegalDateException(date_from)


def filter_city_hotels(hotel, country, city, filters):
    if hotel["city"] != capitalize(city) or hotel["country"] != capitalize(country):
        return False

    return (
        (filters["superchain"] is None or hotel["superchain"] in filters["superchain"])
        and (filters["hotel"] is None or hotel["name"] in filters["hotel"])
        and (filters["type"] is None or hotel["type"] in filters["type"])
        and (filters["min_cost"] is None or filters["min_cost"] <= hotel["cost"])
        and (filters["max_cost"] is None or hotel["cost"] <= filters["max_cost"])
    )
