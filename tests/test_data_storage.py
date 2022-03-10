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
    assert result == temp


def test_create_pulse_datum(data_storage):
    pulse = PulseDatum(device_id=1,
                       assigned_user=1,
                       received_time=datetime.now(),
                       collection_time=datetime.now(),
                       bpm=75)

    result = data_storage.create(pulse)
    assert result == pulse
