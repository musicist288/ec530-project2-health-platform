.. _data-documentation:

Recording Health Data
=====================

Health data, like devices, has two representations, an internal pure-python
class and models specifically tied to certain storage implementations. This
document describes the Datum Models, their relational counterparts, and
an example storage proxy that persists the data to a SQLite database file
specified.

Datum Models
------------
.. currentmodule:: medops.models.device_models

.. autoclass:: DeviceDatum
    :members:

|

.. autoclass:: TemperatureDatum
    :members:

|

.. autoclass:: BloodPressureDatum
    :members:

|

.. autoclass:: GlucometerDatum
    :members:

|

.. autoclass:: PulseDatum
    :members:

|

.. autoclass:: WeightDatum
    :members:

|

.. autoclass:: BloodSaturationDatum
    :members:


Relational Models
-----------------

The models defined in this section correspond to the data models above except
that they are crafted to persist in a relational database. Access to the
database should be managed elsewhere. Medops does provide a :class:`DataStorage`
implementation for storing data in a SQLite database.

.. autoclass:: DeviceDatumModel
    :members:

|

.. autoclass:: TemperatureDatumModel
    :members:

|

.. autoclass:: BloodPressureDatumModel
    :members:

|

.. autoclass:: GlucometerDatumModel
    :members:

|

.. autoclass:: PulseDatumModel
    :members:

|

.. autoclass:: WeightDatumModel
    :members:

|

.. autoclass:: BloodSaturationDatumModel
    :members:

Storage Implementations
-----------------------

.. autoclass:: DataStorage
    :members:
