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


def create_user(client, username="default", role_ids=None):
    if not role_ids:
        role_ids = []

    request_data = dict(
        first_name="Jack",
        last_name="Karowac",
        dob="1997-03-17",
        role_ids=role_ids,
        email=username,
        password="1234"
    )

    return request_data, client.post("/users", json=request_data)

def create_valid_user(client, username="default_username", role_ids=None):
    request_data, resp = create_user(client, username, role_ids)
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


def test_create_user_missing_required_field(client):
    request_data = dict(
        first_name="Jack",
        last_name="Karowac",
        dob="1997-03-17",
        role_ids=[],
        email="test_email",
        password="password"
    )
    for i, field in enumerate(['first_name', 'last_name', 'dob', 'role_ids']):
        request_data['email'] = f'email{str(i)}'
        r = copy.copy(request_data)
        r.pop(field)
        resp = client.post("/users", json=r)
        err_msg = f"{field} was omitted but the user was still created"
        assert resp.status_code == 422, err_msg

        if field == 'role_ids':
            continue
        r = copy.copy(request_data)
        r[field] = None
        resp = client.post("/users", json=r)
        err_msg = f"{field} was blank but the user was still created"
        assert resp.status_code == 422, err_msg

def test_create_user_invalid_date(client):
    request_data = dict(
        first_name="Jack",
        last_name="Karowac",
        dob="invalid_date",
        role_ids=[],
        email="test_email",
        password="unit tests",
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
        role_ids=[admin_id, patient_id],
        email="username",
        password="1234"
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


def test_create_patient_with_relationship(client):
    _, create_resp = create_user_role(client, user_role="Doctor")
    assert create_resp.status_code == 200
    doctor_role = create_resp.json['user_role']['role_id']

    _, create_resp = create_user_role(client, user_role="Patient")
    assert create_resp.status_code == 200
    patient_role = create_resp.json['user_role']['role_id']

    _, resp = create_valid_user(client, username="Doctor", role_ids=[doctor_role])
    assert resp.status_code == 200
    doctor = resp.json['user']

    request_data = dict(
        first_name="Jack",
        last_name="Karowac",
        dob="1997-03-17",
        email="Patient",
        password="1234",
        role_ids=[patient_role],
        medical_staff_ids=[doctor['user_id']]
    )

    resp = client.post("/users", json=request_data)
    assert resp.status_code == 200
    assert 'medical_staff' in resp.json['user']
    assert len(resp.json['user']['medical_staff']) == 1
    assert resp.json['user']['medical_staff'][0]['user_id'] == doctor['user_id']

def test_no_duplicate_usernames(client):
    _, create_resp = create_user_role(client, user_role="Doctor")
    assert create_resp.status_code == 200
    doctor_role = create_resp.json['user_role']['role_id']

    _, resp = create_user(client, username="Doctor", role_ids=[doctor_role])
    assert resp.status_code == 200
    _, resp = create_user(client, username="Doctor", role_ids=[doctor_role])
    assert resp.status_code == 409
    _, resp = create_user(client, username="Doctor2", role_ids=[doctor_role])
    assert resp.status_code == 200

def test_update_patient_with_relationship(client):
    _, create_resp = create_user_role(client, user_role="Doctor")
    assert create_resp.status_code == 200
    doctor_role = create_resp.json['user_role']['role_id']

    _, create_resp = create_user_role(client, user_role="Patient")
    assert create_resp.status_code == 200
    patient_role = create_resp.json['user_role']['role_id']

    _, resp = create_valid_user(client, username="Doctor", role_ids=[doctor_role])
    assert resp.status_code == 200
    doctor = resp.json['user']

    request_data = dict(
        first_name="Jack",
        last_name="Karowac",
        dob="1997-03-17",
        email="Patient",
        password="1234",
        role_ids=[patient_role]
    )

    resp = client.post("/users", json=request_data)
    assert resp.status_code == 200
    assert 'medical_staff' in resp.json['user']
    assert len(resp.json['user']['medical_staff']) == 0

    data = dict(
        first_name="Jack",
        last_name="Karowac",
        dob="1997-03-17",
        role_ids=[patient_role],
        medical_staff_ids=[doctor['user_id']]
    )
    resp = client.post(f"/users/{resp.json['user']['user_id']}", json=data)
    assert resp.json['user']['medical_staff'][0]['user_id'] == doctor['user_id']
