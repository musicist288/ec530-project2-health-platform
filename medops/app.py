"""
This module provides an example Flask application with the API
blueprints hooked up that can be used when hosting the REST API.
"""
from flask import Flask
from .apis import (
    DEVICES_API_BLUEPRINT,
    DATA_API_BLUEPRINT
)

APP = Flask(__name__)
APP.register_blueprint(DEVICES_API_BLUEPRINT, url_prefix="/devices")
APP.register_blueprint(DATA_API_BLUEPRINT, url_prefix="/data")

@APP.route("/")
def index():
    """Default placeholder toot for checking that
    the API works.
    """
    return "Welcome to the MedOps API!"

if __name__ == "__main__":
    APP.run("debug")
