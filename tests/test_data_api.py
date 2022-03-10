from unittest import mock
from datetime import datetime
import os

import pytest
from flask import Flask
from medops import apis, models
from medops.models import device_models

@pytest.fixture()
def client():
    """Sets up a test client"""
    db_filename = 'device_testing.json'
    if os.path.exists(db_filename):
        os.unlink(db_filename)

    app = Flask(__name__)
    app.register_blueprint(apis.DATA_API_BLUEPRINT, url_prefix="/data")
    models.init_db(app, {"DEVICES_FILENAME": db_filename,
                         "DATA_DB_FILENAME": db_filename})

    with app.test_client() as testing_client:
        with app.app_context():
            yield testing_client

    models.deinit(app)

    if os.path.exists(db_filename):
        os.unlink(db_filename)


def test_log_temperatue_data(client):
    request_data = dict(data=[dict(
        device_id=1,
        collection_time=datetime.now().isoformat(),
        data_type="temperature",
        data=dict(deg_c=36),
    )])

    store_mock = apis.data.device_models.store_data = mock.MagicMock()
    resp = client.post("/data/", json=request_data)
    assert resp.status_code == 201
    # Make sure the call was made to store data.
    assert store_mock.call_count == 1
    args = store_mock.call_args[0][0]
    assert isinstance(args[0], device_models.TemperatureDatum)


def test_log_bloodpressure_data(client):
    request_data = dict(data=[dict(
        device_id=1,
        collection_time=datetime.now().isoformat(),
        data_type="blood_pressure",
        data=dict(systolic=120, diastolic=80),
    )])

    store_mock = apis.data.device_models.store_data = mock.MagicMock()
    resp = client.post("/data/", json=request_data)
    assert resp.status_code == 201
    # Make sure the call was made to store data.
    assert store_mock.call_count == 1
    args = store_mock.call_args[0][0]
    assert isinstance(args[0], device_models.BloodPressureDatum)


def test_log_oxygensaturation_data(client):
    request_data = dict(data=[dict(
        device_id=1,
        collection_time=datetime.now().isoformat(),
        data_type="oxygen_saturation",
        data=dict(percentage=38.3),
    )])

    store_mock = apis.data.device_models.store_data = mock.MagicMock()
    resp = client.post("/data/", json=request_data)
    assert resp.status_code == 201
    # Make sure the call was made to store data.
    assert store_mock.call_count == 1
    args = store_mock.call_args[0][0]
    assert isinstance(args[0], device_models.BloodSaturationDatum)


def test_log_glucose_data(client):
    request_data = dict(data=[dict(
        device_id=1,
        collection_time=datetime.now().isoformat(),
        data_type="glucose_level",
        data=dict(mg_dl=6),
    )])

    store_mock = apis.data.device_models.store_data = mock.MagicMock()
    resp = client.post("/data/", json=request_data)
    assert resp.status_code == 201
    # Make sure the call was made to store data.
    assert store_mock.call_count == 1
    args = store_mock.call_args[0][0]
    assert isinstance(args[0], device_models.GlucometerDatum)


def test_log_pulse_data(client):
    request_data = dict(data=[dict(
        device_id=1,
        collection_time=datetime.now().isoformat(),
        data_type="heart_rate",
        data=dict(bpm=90),
    )])

    store_mock = apis.data.device_models.store_data = mock.MagicMock()
    resp = client.post("/data/", json=request_data)
    assert resp.status_code == 201
    # Make sure the call was made to store data.
    assert store_mock.call_count == 1
    args = store_mock.call_args[0][0]
    assert isinstance(args[0], device_models.PulseDatum)


def test_log_weight_data(client):
    request_data = dict(data=[dict(
        device_id=1,
        collection_time=datetime.now().isoformat(),
        data_type="weight",
        data=dict(grams=65039),
    )])

    store_mock = apis.data.device_models.store_data = mock.MagicMock()
    resp = client.post("/data/", json=request_data)
    assert resp.status_code == 201
    # Make sure the call was made to store data.
    assert store_mock.call_count == 1
    args = store_mock.call_args[0][0]
    assert isinstance(args[0], device_models.WeightDatum)


def test_data_type_mismatch(client):
    """Test that says it's reporting weight data but sends temperature"""
    request_data = dict(data=[dict(
        device_id=1,
        collection_time=datetime.now().isoformat(),
        data_type="weight",
        data=dict(deg_c=93.6),
    )])

    store_mock = apis.data.device_models.store_data = mock.MagicMock()
    resp = client.post("/data/", json=request_data)
    assert resp.status_code == 422
    # Make sure the call was not made to store data.
    assert store_mock.call_count == 0


def test_missing_required_fields(client):
    """Test that says it's reporting weight data but sends temperature"""
    request_data = dict(data=[dict(
        collection_time=datetime.now().isoformat(),
        data_type="weight",
        data=dict(grams=23000),
    )])

    store_mock = apis.data.device_models.store_data = mock.MagicMock()
    resp = client.post("/data/", json=request_data)
    assert resp.status_code == 422
    # Make sure the call was not made to store data.
    assert store_mock.call_count == 0

    request_data = dict(data=[dict(
        device_id=0,
        collection_time=datetime.now().isoformat(),
        data=dict(grams=23000),
    )])
    resp = client.post("/data/", json=request_data)
    assert resp.status_code == 422
    # Make sure the call was not made to store data.
    assert store_mock.call_count == 0

    request_data = dict(data=[dict(
        device_id=0,
        collection_time=datetime.now().isoformat(),
        data_type="weight"
    )])
    resp = client.post("/data/", json=request_data)
    assert resp.status_code == 422
    # Make sure the call was not made to store data.
    assert store_mock.call_count == 0


def test_date_parsing(client):
    """Make suer that the API is parsing date strings correctly"""
    now = datetime.now()
    request_data = dict(data=[dict(
        device_id=1,
        collection_time=now.isoformat(),
        data_type="temperature",
        data=dict(deg_c=36),
    )])

    store_mock = apis.data.device_models.store_data = mock.MagicMock()
    resp = client.post("/data/", json=request_data)
    assert resp.status_code == 201
    # Make sure the call was made to store data.
    assert store_mock.call_count == 1
    args = store_mock.call_args[0][0]
    assert args[0].collection_time == now

    # If the date time is not in an iso format,
    # it should not store the data.
    store_mock.reset_mock()
    request_data = dict(data=[dict(
        device_id=1,
        collection_time=now,
        data_type="temperature",
        data=dict(deg_c=36),
    )])
    resp = client.post("/data/", json=request_data)
    assert resp.status_code == 422
    # Make sure the call was made to store data.
    assert store_mock.call_count == 0
