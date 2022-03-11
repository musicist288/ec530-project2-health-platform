import os
from datetime import datetime
import pytest
from medops.models.device_models import (
    DataStorage,
    PulseDatum,
    TemperatureDatum
)

import atexit

FILENAME = "temp_test.db"

def cleanup():
    if os.path.exists(FILENAME):
        os.unlink(FILENAME)


atexit.register(cleanup)

@pytest.fixture
def data_storage():
    data_storage = DataStorage(FILENAME)
    yield data_storage
    data_storage.deinit()


def test_create_temp_datum(data_storage):
    temp = TemperatureDatum(device_id=1,
                            assigned_user=1,
                            received_time=datetime.now(),
                            collection_time=datetime.now(),
                            deg_c=37.2)

    result = data_storage.create(temp)
    # datum_id gets assigned when the device is created.
    # set the attribute for easier equality.
    temp.datum_id = result.datum_id
    assert result == temp


def test_create_pulse_datum(data_storage: DataStorage):
    pulse = PulseDatum(device_id=1,
                       assigned_user=1,
                       received_time=datetime.now(),
                       collection_time=datetime.now(),
                       bpm=75)

    result = data_storage.create(pulse)
    # datum_id gets assigned when the device is created.
    # set the attribute for easier equality.
    pulse.datum_id = result.datum_id
    assert result == pulse

def test_cannot_overwrite_tables(data_storage):
    try:
        data_storage.tables = None
        pytest.fail()
    except Exception:
        pass
