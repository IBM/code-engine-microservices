from app.services import data_handler
from app.errors import tag_not_found, item_not_found
from app.jaeger import Jaeger
from flask import jsonify, request, Blueprint
from datetime import datetime
from pybreaker import CircuitBreaker

hotels_blueprint = Blueprint("hotels_blueprint", __name__)

info_breaker = CircuitBreaker(fail_max=5, reset_timeout=30)
id_breaker = CircuitBreaker(fail_max=5, reset_timeout=30)
breaker = CircuitBreaker(fail_max=5, reset_timeout=30)

context = Jaeger()


def string_to_array(string):
    return string.split(",")


def get_query_param(key, query_data, func):
    if key in query_data.keys():
        if query_data[key] == "NaN":
            return None
        return func(query_data[key])
    return None


@hotels_blueprint.route("/info/<tag>", methods=["GET"])
def filter_list(tag):
    """
    /**
    * GET /api/v1/hotels/info/{filter}
    * @tag Hotel
    * @summary Get filter list
    * @description Gets list of a type to filter Hotel data by.
    * @pathParam {FilterType} filter - The name of the filter to get options for.
    * @response 200 - OK
    * @response 400 - Filter Not Found Error
    * @response 500 - Internal Server Error
    */
    """

    context.start("info", request)
    try:
        data = info_breaker.call(data_handler.get_filter_list, tag, context)
        status_code = 200
    except tag_not_found.TagNotFoundException as e:
        data = {"error": e.args[0]}
        status_code = 400
    except Exception as e:
        data = {"error": e.args[0]}
        status_code = 500
    finally:
        context.stop(status_code)
        return jsonify(data), status_code


@hotels_blueprint.route("/<id>", methods=["GET"])
def get_id(id):
    """
    /**
    * GET /api/v1/hotels/{id}
    * @tag Hotel
    * @summary Get hotel by id
    * @description Gets data associated with a specific Hotel ID.
    * @pathParam {string} id - id of the Hotel
    * @queryParam {string} dateFrom - Date From
    * @queryParam {string} dateTo - Date To
    * @response 200 - OK
    * @response 404 - not found
    * @response 500 - Internal Server Error
    */
    """

    context.start("id", request)
    try:
        query_data = request.args
        data = id_breaker.call(
            data_handler.get_hotel_by_id,
            id,
            {
                "date_from": get_query_param("dateFrom", query_data, parse_date),
                "date_to": get_query_param("dateTo", query_data, parse_date),
            },
            context,
        )
        status_code = 200
    except item_not_found.ItemNotFoundException:
        data = {"error": "not found"}
        status_code = 404
    except Exception as e:
        data = {"error": e.args[0]}
        status_code = 500
    finally:
        context.stop(status_code)
        return jsonify(data), status_code


@hotels_blueprint.route("/<country>/<city>", methods=["GET"])
def get_city(country, city):
    """
    /**
    * GET /api/v1/hotels/{country}/{city}
    * @tag Hotel
    * @summary Get list of hotels
    * @description Gets data associated with a specific city.
    * @pathParam {string} country - Country of the hotel using slug casing.
    * @pathParam {string} city - City of the hotel using slug casing.
    * @queryParam {string} dateFrom - Date From
    * @queryParam {string} dateTo - Date To
    * @queryParam {string} [superchain] - Hotel superchain name.
    * @queryParam {string} [hotel] - Hotel Name.
    * @queryParam {string} [type] - Hotel Type.
    * @queryParam {number} [mincost] - Min Cost.
    * @queryParam {number} [maxcost] - Max Cost.
    * @response 200 - OK
    * @response 500 - Internal Server Error
    */
    """

    context.start("city", request)
    try:
        query_data = request.args
        data = breaker.call(
            data_handler.get_hotels,
            country,
            city,
            {
                "superchain": get_query_param(
                    "superchain", query_data, string_to_array
                ),
                "hotel": get_query_param("hotel", query_data, string_to_array),
                "type": get_query_param("type", query_data, string_to_array),
                "min_cost": get_query_param("mincost", query_data, int),
                "max_cost": get_query_param("maxcost", query_data, int),
                "date_from": get_query_param("dateFrom", query_data, parse_date),
                "date_to": get_query_param("dateTo", query_data, parse_date),
            },
            context,
        )
        status_code = 200
    except Exception as e:
        print(e)
        data = {"error": "Error"}
        status_code = 500
    finally:
        context.stop(status_code)
        return jsonify(data), status_code


def parse_date(date):
    return datetime.strptime(date, "%Y-%m-%d")
