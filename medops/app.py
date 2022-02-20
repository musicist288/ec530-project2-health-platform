"""
This module provides an example Flask application with the API
blueprints hooked up that can be used when hosting the REST API.
"""
from flask import Flask
from .apis import device

APP = Flask(__name__)
APP.register_blueprint(device.DEVICES_API_BLUEPRINT, url_prefix="/devices")

@APP.route("/")
def index():
    """Default placeholder toot for checking that
    the API works.
    """
    return "Welcome to the MedOps API!"

if __name__ == "__main__":
    APP.run("debug")
