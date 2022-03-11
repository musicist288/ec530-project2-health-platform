Gathering Patient Data
=======================

Patient data is recorded from devices that are registered with the system.
Devices must be registered before data can be reported. Once registered, the
device will be assigned a unique identifier assigned to the system.

Reporting Data
--------------

Data can be reported by devices to be recorded by the system. MedOps uses a
polymorphic architecture for recording different types of health data. See the
:ref:`models-header-ref` for more information about the different types. Rather
than a device being restricted to reporting certain types of data, any
registered device can send any type of data it wants, and it will be logged
appropriately such that it can be queried later.


Device Assignment
-----------------
There's nothing about the device that indicates what user has the device
assigned, but when data is recorded, it must be tagged with the user
from whom it was recorded. Rather than put the onus on device manufacturers
to understand how to keep track of user IDs, the device assignment models
should be used to keep track of what devices are assigned to which patients.

Having this separate model provides a few benefits:

* It provides a way to relate subset of data and users based on time. For
  example, if the same user is assigned the same device multiple times over the
  course of a few years, the DeviceAssignment records allows analysts to
  distinguish between different periods of collection.
* When assignment records are persisted over time persisted, it provides a log
  of when devices were assigned to different users.
* It removes the requirement that when devices report data, they have to keep
  track of the user to which its assigned. With this record, the MedOps service
  can keep track of what device is assigned to a user and automatically associate
  the data when the device reports it.


Recording Data
--------------
See :ref:`data-documentation` for information about how data should be reported
by devices.


.. _models-header-ref:

Device and Data Models
----------------------

.. currentmodule:: medops.models.device_models

.. autoclass:: Device
    :members:

|

.. autoclass:: DeviceAssignment
    :members:


Relational Models
-----------------
The device relational models are tightly related to the Device model
and is intended to

.. autoclass:: DeviceModel
    :members:
