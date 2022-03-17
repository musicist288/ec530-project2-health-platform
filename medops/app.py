"""
This module provides an example Flask application with the API
blueprints hooked up that can be used when hosting the REST API.

If you want to run this app as a development server, you'll need the
following environment variables defined:

MONGO_CONNECTION_STRING - The connection string to a mongodb server.
                          MongoDB is requried to use the chat feature.
MONGO_CHAT_DATABASE_NAME - The name of the mongodb database to log chat
                           messages to
SQLITEDB_FILENAME - The file to use as the sqlite databse.

For convenience, you can define them in a `.env` file and they will get
automatically loaded. Then, from the root of this development repository
run: `FLASK_APP=medops.app flak run`
"""
import atexit
import os
import dotenv
from flask import Flask
from .apis import (
    DEVICES_API_BLUEPRINT,
    DATA_API_BLUEPRINT,
    MESSAGES_API_BLUEPRINT,
    USERS_API_BLUEPRINT
)
from .models import init_db, deinit

APP = Flask(__name__)
APP.register_blueprint(DEVICES_API_BLUEPRINT, url_prefix="/devices")
APP.register_blueprint(DATA_API_BLUEPRINT, url_prefix="/data")
APP.register_blueprint(MESSAGES_API_BLUEPRINT, url_prefix="/messages")
APP.register_blueprint(USERS_API_BLUEPRINT, url_prefix="/users")

class Config:
    def __init__(self):
        self.mongo_connection_string = None
        self.mongo_chat_db_name = None
        self.sqlite_db_filename = None

    def load_from_env(self):
        dotenv.load_dotenv()
        self.mongo_connection_string = os.getenv("MONGO_CONNECTION_STRING")
        if not self.mongo_connection_string:
            raise ValueError("Missing environement variable: MONGO_CONNECTION_STRING")

        self.mongo_chat_db_name = os.getenv("MONGO_CHAT_DATABASE_NAME")
        if not self.mongo_chat_db_name:
            raise ValueError("Missing environement variable: MONGO_CHAT_DATABASE_NAME")

        self.sqlite_db_filename = os.getenv("SQLITEDB_FILENAME")
        if not self.sqlite_db_filename:
            raise ValueError("Missing environment variable SQLITEDB_FILENAME")

    def init_app(self, app, from_env=False):
        if from_env:
            self.load_from_env()

        init_db(app, {
            "DEVICES_FILENAME": self.sqlite_db_filename,
            "DATA_DB_FILENAME": self.sqlite_db_filename,
            "MONGO_CONNECTION_STRING": self.mongo_connection_string,
            "MONGO_DATABASE": self.mongo_chat_db_name,
        })


@APP.route("/")
def index():
    """Default placeholder toot for checking that
    the API works.
    """
    return "Welcome to the MedOps API!"


def default_app():
    config = Config()
    config.init_app(APP, from_env=True)
    atexit.register(deinit, APP)
    return APP

if __name__ == "__main__":
    APP = default_app()
    APP.run("debug")
