"""
    Models contain the in-memory storage data
"""
from pathlib import Path
from .device_models import DeviceStorage
from .device_models import Device # noqa: F401
from .device_models import DeviceType # noqa: F401

from flask import current_app

def init_db(app, config):
    """Initialize the current application instance with the loaded
    config.

    Parameters
    ----------
    app : flask.Flask
        The flask app to configure.
    config : dict
        The application configuration.
    """
    db_file = config["DB_FILENAME"]

    if isinstance(db_file, str):
        db_file = Path(db_file)

    app.config['STORAGE'] = DeviceStorage(db_file)

def get_storage() -> DeviceStorage:
    """Return the configured storage
    """
    return current_app.config['STORAGE']
