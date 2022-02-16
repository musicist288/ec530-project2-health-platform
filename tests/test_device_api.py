import copy
import os

import pytest
from flask import Flask
from medops import apis, models

@pytest.fixture()
def client():
    """Sets up a test client
    """
    db_filename = 'device_testing.json'
    if os.path.exists(db_filename):
        os.unlink(db_filename)

    app = Flask(__name__)
    app.register_blueprint(apis.DEVICES_API_BLUEPRINT, url_prefix="/devices")
    models.init_db(app, {"DEVICES_FILENAME": db_filename})

    with app.test_client() as testing_client:
        with app.app_context():
            yield testing_client

    if os.path.exists(db_filename):
        os.unlink(db_filename)


def create_valid_device(client):
    request_data = dict(
        name="Thermometer-0001",
        date_of_purchase="2021-03-22",
        serial_number=None,
        current_firmware_version="1.0.0"
    )
    resp = client.post("/devices/", json=request_data)
    assert resp.status_code == 200
    return request_data, resp


def test_create_model_happy(client):
    request_data, resp = create_valid_device(client)
    data = resp.json
    fields = [
        'name',
        'date_of_purchase',
        'serial_number',
        'current_firmware_version'
    ]

    for field in fields:
        assert data[field] == request_data[field]

    assert data['device_id'] >= 0

def test_create_device_missing_required_fields(client):
    request_data = dict(
        # Omit name which is a required field.
        # name="Thermometer-0001",
        device_type=1,
        date_of_purchase="2021-03-22",
        serial_number=None,
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

def test_create_device_empty_required_field(client):
    request_data = dict(
        # Omit name which is a required field.
        name="",
        date_of_purchase="2021-03-22",
        serial_number=None,
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


def test_read_device(client):
    _, data = create_valid_device(client)
    device_id = data.json["device_id"]
    assert isinstance(device_id, int)
    response = client.get("/devices/%d" % device_id)
    assert response.status_code == 200
    # Get should return the same data as when
    # the devices is created.
    assert response.json == data.json


def test_read_not_found(client):
    response = client.get("/devices/1234")
    assert response.status_code == 404


def test_read_device_invalid_id(client):
    response = client.get("/devices/abc")
    assert response.status_code == 404


def test_delete_device_not_found(client):
    response = client.delete("/devices/1")
    assert response.status_code == 404


def test_delete_device(client):
    _, resp = create_valid_device(client)
    device = f"/devices/{resp.json['device_id']}"
    response = client.delete(device)
    assert response.status_code == 200

    response = client.get(device)
    assert response.status_code == 404


def test_update_device(client):
    _, resp = create_valid_device(client)
    device_path = f"/devices/{resp.json['device_id']}"
    data = copy.deepcopy(resp.json)
    data['serial_number'] = "testing"

    resp = client.put(device_path, json=data)
    assert resp.status_code == 200
    assert resp.json == data

    # Make sure it persisted and is returned
    # with the updated fields
    resp = client.get(device_path)
    assert resp.status_code == 200
    assert resp.json == data


def test_update_device_invalid(client):
    request_data, resp = create_valid_device(client)
    device_path = f"/devices/{resp.json['device_id']}"
    data = copy.deepcopy(resp.json)
    # You're not allowed to update hte device id
    data['device_id'] += 1
    data['name'] = "Another name"

    before = client.get(device_path)
    resp = client.put(device_path, json=data)
    assert resp.status_code == 422
    after = client.get(device_path)
    # Make sure it wasn't updated
    assert before.json == after.json
