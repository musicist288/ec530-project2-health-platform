"""
This module contains the models for how data is defined in memory
when loaded from the data store.
"""
from __future__ import annotations

from typing import (
    Optional,
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
class Device:
    """The `Device` model represents the metadata associated with a device
    that can be collect data from users. Note that the device does not indicate
    anything about what data is collected from the device. When recording data
    the device id should be tagged by the recorded data. See the Data


    Parameters
    ----------
        device_id : int
            An internal identifier for the device. This field will be auto-generated
            when a new device is created.

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
    """
    device_id: int
    current_firmware_version: Optional[str]
    date_of_purchase: Optional[datetime]
    serial_number: Optional[str]
    mac_address: Optional[str]
    # These fields are validated by property
    name: str

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

    def to_dict(self) -> dict:
        """Convert the model into a dict representation for serialization.

        Returns
        -------
        A dictionary with keys/value pairs of the device attributes
        """
        return asdict(self)


@dataclass
class DeviceDatum:
    """Base class for different device datum types. This class should
    not be used directly.

    Parameters
    ----------
        device_id : int
            The identifier of the device that recired that recorded the data.
            This field is optional.

        assigned_user : int
            The user ID of the patient from which the datum was collected.

        received_time : datetime
            The datetime stamp when the datum was received by the system.

        collection_time : datetime
            The datetime stamp when the datum was collected on the device.
    """
    device_id: int
    assigned_user: int
    received_time: datetime
    collection_time: datetime

    def to_dict(self) -> dict:
        """Convert the model into a dict representation for serialization.

        Returns
        -------
        A dictionary with keys/value pairs of the device attributes
        """
        return asdict(self)

    def to_json(self) -> dict:
        """Converts the model and values into a json serializeable dictionary

        Returns
        -------
        A dictionary where all key/value pairs are JSON serializable.
        """
        data = self.to_dict()
        data['received_time'] = self.received_time.isoformat()
        data['collection_time'] = self.collection_time.isoformat()
        return data

    @classmethod
    def from_json(cls, data: dict) -> DeviceDatum:
        """Instantiate a DeviceDatum object from a json dict.

        Parameters
        ----------
        data : dict
            A dictionary of key value pairs that are json serializeable

        Returns
        -------
        An instance of the device datum class.
        """

        received_time = datetime.fromisoformat(data.pop('received_time'))
        collection_time = datetime.fromisoformat(data.pop('collection_time'))
        return cls(**data,
                   received_time=received_time,
                   collection_time=collection_time)


@dataclass
class TemperatureDatum(DeviceDatum):
    """A temperature datum

    See :py:class:`~DeviceDatum` for the other constructor parameter descriptions.

    Parameters
    ----------
    deg_c : float
        Temperature value in degrees C
    """
    deg_c: float


@dataclass
class BloodPressureDatum(DeviceDatum):
    """A blood pressure datum

    See :py:class:`~DeviceDatum` for the other constructor parameter descriptions.

    Parameters
    ----------
    systolic : float
        The systolic measurement
    diastolic : float
        The diastolic measurement
    """
    systolic: float
    diastolic: float


@dataclass
class GlucometerDatum(DeviceDatum):
    """A glucose level reading

    See :py:class:`~DeviceDatum` for the other constructor parameter descriptions.

    Parameters
    ----------
    mg_dl : int
        The blood sugar level in milligrams per deciliter
    """
    mg_dl: int


@dataclass
class PulseDatum(DeviceDatum):
    """A heart rate dataum

    See :py:class:`~DeviceDatum` for the other constructor parameter descriptions.

    Parameters
    ----------
    bpm : int
        The measured heart rate in beats per minute.
    """
    bpm: int


@dataclass
class WeightDatum(DeviceDatum):
    """A weight datum

    See :py:class:`~DeviceDatum` for the other constructor parameter descriptions.

    Parameters
    ----------
    grams : int
        Weight record in grams
    """
    grams: int


@dataclass
class BloodSaturationDatum(DeviceDatum):
    """Blood saturation datum

    See :py:class:`~DeviceDatum` for the other constructor parameter descriptions.

    Parameters
    ----------
    percentage : float
        The blood saturation percentage.
    """
    percentage: float


@dataclass
class DeviceAssignment:
    """The device assignment is a record of time periods when a device has been
    assigned to a user. Data collected during this time.

    Parameters
    ----------
    device_id : int
        The ID of the device assigned

    patient_id : int
        The user ID of the patient to whom the device is assigned.

    assigner_id : int
        The user ID of the medical professional who authorized the device
        to be assigned to the patient.

    date_assigned : datetime
        The start date and time when the user is assigned the device.

    date_returned : Optional[datetime]
        The date when the device is no longer recording data from the patient.
        This field should be set to None
    """

    device_id: int
    patient_id: int
    assigner_id: int
    date_assigned: datetime
    date_returned: Optional[datetime]


# XXX: This is just a placeholder until there is a proper
# database backend.
class Storage:

    model = None
    id_field = None

    def __init__(self, filename: Path):
        self.filename = filename
        self.records = []

        # Load the file.
        self._loaded = False
        self._next_id = None
        self._load()

    def _save(self):
        with self.filename.open("w") as handle:
            data = [device.to_dict() for device in self.records]
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
                    self.records = [self.model(**d) for d in data]

                self._next_id = max([getattr(d, self.id_field) for d in self.records])
            else:
                self._next_id = 1

            self._loaded = True

    def query(self):
        pass

    def get(self, record_id: int) -> Optional[Device]:
        to_return = None

        for device in self.records:
            if getattr(device, self.id_field) == record_id:
                to_return = copy.deepcopy(device)

        return to_return

    def create(self, model):
        if getattr(model, self.id_field) is not None:
            raise ValueError(f"{self.id_filed} is an autoincrement file. It must be None when created")

        setattr(model, self.id_field, self._next_id)
        self._next_id += 1

        # Create a deep copy of the device so user modifications
        # don't change anything.
        for_storage = copy.deepcopy(model)
        self.records.append(for_storage)
        self._save()
        return model

    def update(self, model):
        if getattr(model, self.id_field) is None:
            raise ValueError("Device does not exist.")

        for_storage = copy.deepcopy(model)
        # remove the old one
        models = [d for d in self.records if getattr(d, self.id_field) != getattr(model, self.id_field)]
        models.append(for_storage)
        self.records = models
        self._save()
        return model

    def delete(self, record_id: int) -> bool:
        models = [d for d in self.records if getattr(d, self.id_field) != record_id]
        deleted = len(models) < len(self.records)
        self.records = models
        self._save()
        return deleted


class DeviceStorage(Storage):
    model = Device
    id_field = "device_id"


def store_data(data: list[DeviceDatum]):
    pass

class DataStorage:

    def store(data: list[DeviceDatum]):
        pass
