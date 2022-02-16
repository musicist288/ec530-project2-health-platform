"""
    Models contain the in-memory storage data
"""
from pathlib import Path
from .device_models import DeviceStorage, Storage
from .device_models import Device # noqa: F401

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
    devices_file = config["DEVICES_FILENAME"]
    if isinstance(devices_file, str):
        devices_file = Path(devices_file)

    app.config['STORAGE'] = {"devices": DeviceStorage(devices_file)}

def get_storage(name) -> Storage:
    """Return the configured storage
    """
    if name not in current_app.config['STORAGE']:
        raise ValueError(f"Storage for {name} does not exist")

    return current_app.config['STORAGE'][name]
