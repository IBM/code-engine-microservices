import time
from flask import request
from prometheus_client import Counter, Summary

NUM_OF_REQUESTS = Counter("numOfRequests", "Number of requests made", ["method"])

PATHS_TAKEN = Counter("pathsTaken", "Paths taken in the app", ["path"])

RESPONSE = Summary("responses", "Response time in millis", ["method", "path", "status"])


def before_request():
    request._prometheus_metrics_request_start_time = time.time()


def after_request(response):
    request_time = time.time() - request._prometheus_metrics_request_start_time
    if request.endpoint and "hotels_blueprint" in request.endpoint:
        RESPONSE.labels(request.method, request.path, response.status_code).observe(
            request_time
        )
        NUM_OF_REQUESTS.labels(request.method).inc()
        PATHS_TAKEN.labels(request.path).inc()
    return response


def register_metrics(app):
    app.before_request(before_request)
    app.after_request(after_request)
