import copy
import pytest
from flask import Flask
from medops import apis, models
import atexit
import os

FILENAME = "user_testing.json"

def cleanup():
    if os.path.exists(FILENAME):
        os.unlink(FILENAME)

atexit.register(cleanup)

@pytest.fixture()
def client():
    """Sets up a test client
    """
    db_filename = FILENAME
    app = Flask(__name__)
    app.register_blueprint(apis.USERS_API_BLUEPRINT, url_prefix="/users")
    models.init_db(app, {"USERS_DB_FILENAME": db_filename})

    with app.test_client() as testing_client:
        with app.app_context():
            yield testing_client

    models.deinit(app)
    cleanup()


def create_valid_user(client):
    request_data = dict(
        first_name="Jack",
        last_name="Karowac",
        dob="1997-03-17",
        role_ids=[]
    )
    resp = client.post("/users", json=request_data)
    assert resp.status_code == 200, resp.json['errors']
    return request_data, resp


def test_create_user_happy(client):
    request_data, resp = create_valid_user(client)
    data = resp.json
    fields = [
        'first_name',
        'last_name',
        'dob',
    ]

    for field in fields:
        assert data['user'][field] == request_data[field]

    for expected, role in zip(request_data['role_ids'], data['user']['roles']):
        assert expected == role['role_id']

    assert data['user']['user_id'] >= 0


def test_create_user_missing_requried_field(client):
    request_data = dict(
        first_name="Jack",
        last_name="Karowac",
        dob="1997-03-17",
        role_ids=[]
    )
    for field in ['first_name', 'last_name', 'dob', 'role_ids']:
        r = copy.copy(request_data)
        r.pop(field)
        resp = client.post("/users", json=r)
        err_msg = f"{field} was omitted but the user was still created"
        assert resp.status_code == 422, err_msg


def test_create_user_invalid_date(client):
    request_data = dict(
        first_name="Jack",
        last_name="Karowac",
        dob="invalid_date",
        role_ids=[]
    )
    resp = client.post("/users", json=request_data)
    assert resp.status_code == 422


def test_delete_user(client):
    request_data, resp = create_valid_user(client)
    user_id = resp.json['user']['user_id']
    resp = client.delete(f"/users/{user_id}")
    assert resp.status_code == 201

    resp = client.get(f"/users/{user_id}")
    assert resp.status_code == 404


def test_get_user(client):
    request_data, create_resp = create_valid_user(client)
    user_id = create_resp.json['user']["user_id"]

    get_resp = client.get(f"/users/{user_id}")
    assert get_resp.status_code == 200
    assert get_resp.json['user'] == create_resp.json['user']


def test_get_user_dne(client):
    request_data, create_resp = create_valid_user(client)
    user_id = create_resp.json['user']["user_id"]
    get_resp = client.get(f"/users/{user_id+1}")
    assert get_resp.status_code == 404


def create_user_role(client, user_role="Admin"):
    request_data = dict(role_name=user_role)
    resp = client.post("/users/roles", json=request_data)
    assert resp.status_code == 200
    return request_data, resp


def test_create_and_get_user_role(client):
    request_data, create_resp = create_user_role(client)
    role_id = create_resp.json['user_role']['role_id']
    assert role_id >= 0

    resp = client.get(f"/users/roles/{role_id}")
    assert resp.status_code == 200
    assert resp.json['user_role']['role_name'] == request_data['role_name']
    assert resp.json['user_role']['role_id'] == role_id


def test_update_user_role(client):
    request_data, create_resp = create_user_role(client)
    role_id = create_resp.json['user_role']['role_id']
    assert role_id >= 0

    request_data['role_name'] = "Administrator"
    resp = client.post(f"/users/roles/{role_id}", json=request_data)
    assert resp.status_code == 200
    assert resp.json['user_role']['role_name'] == request_data['role_name']
    assert resp.json['user_role']['role_id'] == role_id

    resp = client.get(f"/users/roles/{role_id}")
    assert resp.json['user_role']['role_name'] == request_data['role_name']


def test_update_roles_for_user(client):
    _, admin_resp = create_user_role(client, user_role="Admin")
    _, patient_resp = create_user_role(client, user_role="Patient")

    admin_id = admin_resp.json['user_role']['role_id']
    patient_id = patient_resp.json['user_role']['role_id']

    request_data = dict(
        first_name="Jack",
        last_name="Karowac",
        dob="1997-03-17",
        role_ids=[admin_id, patient_id]
    )

    resp = client.post("/users", json=request_data)
    assert resp.status_code == 200
    roles = resp.json['user']['roles']
    assert len(roles) == len(request_data['role_ids'])
    role_ids = set([r['role_id'] for r in roles])
    expected_ids = set(request_data['role_ids'])
    assert role_ids == expected_ids

    user_id = resp.json['user']['user_id']

    # Removing patient role
    request_data['role_ids'] = [admin_id]
    resp = client.post(f"/users/{user_id}", json=request_data)
    assert resp.status_code == 200
    roles = resp.json['user']['roles']
    assert len(roles) == len(request_data['role_ids'])
    role_ids = set([r['role_id'] for r in roles])
    expected_ids = set(request_data['role_ids'])
    assert role_ids == expected_ids

    # # Remove admin role, add patient role
    request_data['role_ids'] = [patient_id]
    resp = client.post(f"/users/{user_id}", json=request_data)
    assert resp.status_code == 200
    roles = resp.json['user']['roles']
    assert len(roles) == len(request_data['role_ids'])
    role_ids = set([r['role_id'] for r in roles])
    expected_ids = set(request_data['role_ids'])
    assert role_ids == expected_ids

    # # Remove all roles
    request_data['role_ids'] = []
    resp = client.post(f"/users/{user_id}", json=request_data)
    assert resp.status_code == 200
    roles = resp.json['user']['roles']
    assert len(roles) == len(request_data['role_ids'])
    role_ids = set([r['role_id'] for r in roles])
    expected_ids = set(request_data['role_ids'])
    assert role_ids == expected_ids

    # # Add back both roles
    request_data['role_ids'] = [admin_id, patient_id]
    resp = client.post(f"/users/{user_id}", json=request_data)
    assert resp.status_code == 200
    roles = resp.json['user']['roles']
    assert len(roles) == len(request_data['role_ids'])
    role_ids = set([r['role_id'] for r in roles])
    expected_ids = set(request_data['role_ids'])
    assert role_ids == expected_ids
