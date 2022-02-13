"""
    This module defines the blueprint for the devices API that can be integrated
    into a Flask app. It is intentionally declared separately so it is up to the
    operations team whether they want to host this API separately or in
    conjunction with another set of APIs.
"""

from flask import (
    Blueprint,
    Response,
    request,
    make_response,
    jsonify
)

from .. import models
from typing import Tuple

def error_response(errors: list[str]) -> Tuple[Response, int]:
    return jsonify(errors=errors, count=len(errors)), 422


# TODO: Make this configurable
DEVICES_API_BLUEPRINT = Blueprint("devices", __name__)

@DEVICES_API_BLUEPRINT.route("/", methods=["GET"])
def device_query():
    pass

@DEVICES_API_BLUEPRINT.route("/", methods=["POST"])
def device_create():
    """Create a new device.

    When registered with a Flask app, this method will handle when the
    user sends a HTTP PUT request to <base_uri>/devices/<device_id>

    See the HTTP API documentation for information about the payload
    structure.
    """
    data = request.get_json()
    if data is None:
        # The request data format was not valid.
        return make_response("Invalid JSON request."), 400

    # Create an empty errors array
    errors = []
    required_fields = ["device_type", "name"]
    for field in required_fields:
        if field not in data.keys():
            errors.append(f"Missing required field: {field}")

    if errors:
        return error_response(errors)

    device = models.get_storage().create(models.Device(
        device_id=None,
        name=data["name"],
        device_type=data["device_type"],
        current_firmware_version=data.get("current_firmware_version", None),
        assigned_user=data.get("assigned_user"),
        assigner=data.get("assigner", None),
        mac_address=data.get("mac_address", None),
        serial_number=data.get("serial_number", None),
        date_of_purchase=data.get("date_of_purchase", None),
    ))

    return jsonify(device)


@DEVICES_API_BLUEPRINT.route("/<device_id>", methods=["PUT"])
def device_update(device_id):
    """Update an existing device.

    When registered with a Flask app, this method will handle when the
    user sends a HTTP PUT request to <base_uri>/devices/<device_id>

    See the HTTP API documentation for information about the payload
    structure.

    Parameters
    ----------
        device_id: int
            The ID of the device to update
    """
    data = request.get_json()
    if data is None:
        # The request data format was not valid.
        return make_response("Invalid JSON request."), 400

    # Create an empty errors array
    errors = []

    if errors:
        return error_response(errors)


@DEVICES_API_BLUEPRINT.route("/<device_id>", methods=["DELETE"])
def device_delete(device_id):
    pass
