"""
This module contains the models for how data is defined in memory
when loaded from the data store.
"""

from typing import (
    Optional,
    Union
)
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
import copy
import json


@dataclass
class User:
    """
        Placeholder model for when users are in place.
    """
    pass

# TODO: Figure out how to get the format string to render correctly
# when generating documentation
DataTypes = set([
    "integer",
    "float",
    "number_array",
    "string"
])


@dataclass
class DeviceType:
    """Model class for the device type

    Parameters
    ----------
        device_type_id : int
            The identifier for the device

        name : str
            Short name for the type of device

        data_type : str
            The type of data expected from the device. The data
            type must be one of the following supported types:

            - "integer",
            - "float",
            - "number_array",
            - "string"
    """
    device_type_id: int
    name: str
    data_type: str


@dataclass
class Device:
    """Model class for medical devices

    Parameters
    ----------
        device_id : int
            The identifier for the device.

        device_type : DeviceType
            Metadata about the type of data the device can collect.

        current_firmware_version : str
            Latest information about what firmware version was loaded
            on the device.

        date_of_purchase : Optional[datetime]
            The date when the device was purchased, if available

        serial_number : Optional[str]
            The serial number of the device.

        mac_address : Optional[str]
            If the device is a networked device, this field should
            contain the MAC address.

        assigned_user : Optional[User]
            The user for which the device is currently collecting information.

        assigner : Optional[User]
            The medical profession who assigned the device to the assigned user.

        name : str
            A summary field for describing the name of the device.
    """
    device_id: int
    device_type: DeviceType
    current_firmware_version: str
    date_of_purchase: Optional[datetime]
    serial_number: Optional[str]
    mac_address: Optional[str]
    assigned_user: Optional[User]
    assigner: Optional[Union[int, User]]
    name: str

    def to_dict(self) -> dict:
        """Convert the model into a dict representation for serialization

        Returns
        -------
        A dictionary with keys/value pairs of the device attributes
        """

        return dict(device_id=self.device_id,
                    device_type=self.device_type,
                    current_firmware_version=self.current_firmware_version,
                    date_of_purchase=self.date_of_purchase,
                    serial_number=self.serial_number,
                    mac_address=self.mac_address,
                    assigned_user=self.assigned_user,
                    assigner=self.assigner,
                    name=self.name)


# XXX: This is just a placeholder until there is a proper
# database backend.
class DeviceStorage:

    def __init__(self, filename: Path):
        self.filename = filename
        self.devices = []

        # Load the file.
        self._loaded = False
        self._next_id = None
        self._load()

    def _save(self):
        with self.filename.open("w") as handle:
            data = [device.to_dict() for device in self.devices]
            json.dump(data, handle)

        if not self._loaded:
            self._loaded = True

        if self._next_id is None:
            self._next_id = 1

    def _load(self):
        if not self._loaded:
            if self.filename.exists():
                with self.filename.open("r") as handle:
                    data = json.load(handle)
                    self.devices = [Device(**d) for d in data]

                self._next_id = max([d.device_id for d in self.devices])
            else:
                self._next_id = 1

            self._loaded = True

    def query(self):
        pass

    def get(self, device_id: int) -> Optional[Device]:
        to_return = None

        for device in self.devices:
            if device.device_id == device_id:
                to_return = copy.deepcopy(device)

        return to_return

    def create(self, device: Device) -> Device:
        if device.device_id is not None:
            raise ValueError("device_id is an autoincrement file. It must be None when created")

        device.device_id = self._next_id
        self._next_id += 1

        # Create a deep copy of the device so user modifications
        # don't change anything.
        for_storage = copy.deepcopy(device)
        self.devices.append(for_storage)
        self._save()
        return device

    def update(self, device: Device) -> Device:
        if device.device_id is None:
            raise ValueError("Device does not exist.")

        for_storage = copy.deepcopy(device)
        # remove the old one
        devices = [d for d in self.devices if d.device_id != device.device_id]
        devices.append(for_storage)
        self.devices = devices
        self._save()
        return device

    def delete(self, device_id: int) -> bool:
        devices = [d for d in self.devices if d.device_id != device_id]
        deleted = len(devices) < len(self.devices)
        self.devices = deleted
        self._save()
        return deleted
