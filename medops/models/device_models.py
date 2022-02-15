"""
This module contains the models for how data is defined in memory
when loaded from the data store.
"""

from typing import (
    Optional
)
from datetime import datetime
from dataclasses import (
    dataclass,
    asdict
)
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
# when generating documentation.
DataTypes = set([
    "integer",
    "float",
    "number_array",
    "string"
])

@dataclass
class DeviceType:
    """The DeviceType model classifies the type of device and what
    data format is represented from that device.

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

    def to_dict(self) -> dict:
        """Convert the model into a dict representation for serialization.

        Returns
        -------
        A dictionary with keys/value pairs of the device attributes
        """
        return asdict(self)


@dataclass
class Device:
    """The `Device` model represents the metadata associated with a device
    that can be collect data from users. When creating a device, you must
    provide an approriate `device_type`. The `device_type` is what governs what
    kind of data is collected from the device. The assumption here is that each
    device can only report one type of data. If a device needs to report multiple
    types of data (for example, the same can measure heart rate and blood pressure),
    the device should be entered twice, one for each device type. If you need to
    associate the data later, make sure to enter the `serial_number` field.

    Parameters
    ----------
        device_id : int
            An internal identifier for the device. This field will be auto-generated
            when a new device is created.

        device_type : DeviceType
            Metadata about the type of data the device can collect. This field
            is required.

        name : str
            A user facing name for the device.

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

    """
    device_id: int
    current_firmware_version: Optional[str]
    date_of_purchase: Optional[datetime]
    serial_number: Optional[str]
    mac_address: Optional[str]
    assigned_user: Optional[int]
    assigner: Optional[int]
    # These fields are validated by property
    name: str
    device_type: int

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value: str):
        if not isinstance(value, str):
            raise ValueError("name must be a string.")
        if not value.strip():
            raise ValueError("name cannot be blank.")
        self.__name = value

    @property
    def device_type(self):
        return self.__device_type

    @device_type.setter
    def device_type(self, value: int):
        if not isinstance(value, int):
            raise ValueError("device_type must be an integer")
        self.__device_type = value

    def to_dict(self) -> dict:
        """Convert the model into a dict representation for serialization.

        Returns
        -------
        A dictionary with keys/value pairs of the device attributes
        """
        return asdict(self)


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
        self.devices = devices
        self._save()
        return deleted
