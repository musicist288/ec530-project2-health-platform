import pytest
import os

from flask import Flask
from medops import apis, models

@pytest.fixture(scope="module")
def client():
    db_filename = 'device_testing.json'
    if os.path.exists(db_filename):
        os.unlink(db_filename)

    app = Flask(__name__)
    app.register_blueprint(apis.DEVICES_API_BLUEPRINT, url_prefix="/devices")
    models.init_db(app, {"DB_FILENAME": db_filename})

    with app.test_client() as testing_client:
        with app.app_context():
            yield testing_client

    if os.path.exists(db_filename):
        os.unlink(db_filename)


def test_create_model_happy(client):
    request_data = dict(
        name="Thermometer-0001",
        device_type={"id": 1},
        date_of_purchase="2021-03-22",
        serial_number=None,
        assigned_user=None,
        assigner=None,
        current_firmware_version="1.0.0"
    )
    resp = client.post("/devices/", json=request_data)

    assert resp.status_code == 200
    data = resp.json
    fields = [
        'name',
        'device_type',
        'date_of_purchase',
        'serial_number',
        'assigned_user',
        'assigner',
        'current_firmware_version'
    ]

    for field in fields:
        assert data[field] == request_data[field]

def test_create_device_missing_required_fields(client):
    request_data = dict(
        # Omit name which is a required field.
        # name="Thermometer-0001",
        device_type={"id": 1},
        date_of_purchase="2021-03-22",
        serial_number=None,
        assigned_user=None,
        assigner=None,
        current_firmware_version="1.0.0"
    )
    resp = client.post("/devices/", json=request_data)

    assert resp.status_code == 422
    assert "errors" in resp.json
    errors = resp.json['errors']
    assert len(errors) == 1
    assert "name" in errors[0]
    assert "count" in resp.json
    assert resp.json["count"] == len(errors)
