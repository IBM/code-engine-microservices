from app.services.data_handler import readiness_check
from flask import Blueprint

health_blueprint = Blueprint("health_blueprint", __name__)


@health_blueprint.route("/live", methods=["GET"])
def live():
    """
    /**
    * GET /live
    * @description Liveness check to make sure service is available
    * @response 200 - OK
    */
    """

    return "OK", 200


@health_blueprint.route("/ready", methods=["GET"])
def ready():
    """
    /**
    * GET /ready
    * @description Readiness check to make sure service and all connected external service calls are available
    * @response 200 - OK
    * @response 503 - Service Unavailable
    */
    """

    is_healthy = readiness_check()
    if is_healthy:
        return "OK", 200
    return "Service Unavailable", 503
