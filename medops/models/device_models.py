"""
This module contains the models for how data is defined in memory
when loaded from the data store.
"""
from __future__ import annotations

import os
from typing import (
    Optional,
)
from datetime import datetime
from dataclasses import (
    dataclass,
    asdict
)
from pathlib import Path

from peewee import (
    SqliteDatabase,
    DateTimeField,
    IntegerField,
    FloatField,
    CharField,
    ForeignKeyField,
    AutoField
)

from .base import (
    BaseModel,
    register_table
)

TABLES = []

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


class Storage:
    """An abstract interface class for storage proxies"""

    def __init__(self, filename: Path):
        pass

    def query(self):
        raise NotImplementedError()

    def get(self, record_id: int) -> Optional[Device]:
        raise NotImplementedError()

    def create(self, model):
        raise NotImplementedError()

    def update(self, model):
        raise NotImplementedError()

    def delete(self, record_id: int) -> bool:
        raise NotImplementedError()


def store_data(data: list[DeviceDatum]):
    pass


@register_table(TABLES)
class DeviceModel(BaseModel):
    device_id = AutoField()
    name = CharField(unique=True)
    current_firmware_version = CharField(null=True)
    date_of_purchase = DateTimeField(null=True)
    serial_number = CharField(null=True)
    mac_address = CharField(null=True, max_length=100)


@register_table(TABLES)
class DeviceDatumModel(BaseModel):
    device_id = ForeignKeyField(DeviceModel, backref="data")
    assigned_user = IntegerField(null=False)
    received_time = DateTimeField(null=False)
    collection_time = DateTimeField(null=False)


@register_table(TABLES)
class TemperatureDatumModel(DeviceDatumModel):
    deg_c = FloatField(null=False)


@register_table(TABLES)
class BloodPressureDatumModel(DeviceDatumModel):
    systolic = FloatField()
    diastolic = FloatField()


@register_table(TABLES)
class GlucometerDatumModel(DeviceDatumModel):
    mg_dl = IntegerField()


@register_table(TABLES)
class PulseDatumModel(DeviceDatumModel):
    bpm = IntegerField()


@register_table(TABLES)
class WeightDatumModel(DeviceDatumModel):
    grams = IntegerField()


@register_table(TABLES)
class BloodSaturationDatumModel(DeviceDatumModel):
    percentage = FloatField()


def _device_from_model(model: DeviceModel) -> Device:
    return Device(
        device_id=model.device_id,
        current_firmware_version=model.current_firmware_version,
        date_of_purchase=model.date_of_purchase,
        serial_number=model.serial_number,
        mac_address=model.mac_address,
        name=model.name
    )


def _model_from_device(device: Device) -> DeviceModel:
    return DeviceModel(
        current_firmware_version=device.current_firmware_version,
        date_of_purchase=device.date_of_purchase,
        serial_number=device.serial_number,
        mac_address=device.mac_address,
        name=device.name
    )


class DeviceStorage:
    dataclass = Device
    model = DeviceModel
    id_field = "device_id"

    def __init__(self, devices_file):
        exists = os.path.exists(devices_file)
        self.database = SqliteDatabase(devices_file)
        self.database.bind(TABLES)
        self.database.connect()

        if not exists:
            self.database.create_tables(TABLES)

    def deinit(self):
        if self.database:
            self.database.close()

    def get(self, record_id: int) -> Optional[Device]:
        query = DeviceModel.select().where(DeviceModel.device_id == record_id)
        if query.count() == 0:
            return None

        model: DeviceModel = query[0]
        return _device_from_model(model)

    def create(self, device: Device) -> Device:
        if device.device_id is not None:
            raise ValueError("device_id must be None when creating a new device.")

        model = _model_from_device(device)
        model.save()
        return _device_from_model(model)

    def update(self, device: Device) -> Device:
        query = DeviceModel.select().where(DeviceModel.device_id == device.device_id)
        if not query.count():
            raise ValueError(f"Device {device.device_id} does not exist.")

        model = query[0]
        model.name = device.name
        model.current_firmware_version = device.current_firmware_version
        model.date_of_purchase = device.date_of_purchase
        model.serial_number = device.serial_number
        model.mac_address = device.mac_address
        model.save()
        return _device_from_model(model)

    def delete(self, record_id: int) -> bool:
        query = DeviceModel.delete().where(DeviceModel.device_id == record_id)
        n_rows_deleted = query.execute()
        return n_rows_deleted >= 1
