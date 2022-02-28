import pytest
from unittest import mock
from flask import Flask
from medops import apis, models

@pytest.fixture()
def client():
    """Sets up a test client
    """

    app = Flask(__name__)
    app.register_blueprint(apis.MESSAGES_API_BLUEPRINT, url_prefix="/messages")
    models.chat_model.pymongo.MongoClient = mock.MagicMock()
    models.init_db(app, {
        "MONGO_CONNECTION_STRING": "testing",
        "MONGO_DATABASE": "testdatabase"

    })

    with app.test_client() as testing_client:
        with app.app_context():
            store = models.get_storage("messages")
            store.database.__getitem__.return_value.count_documents.return_value = 1
            yield testing_client


def test_post_valid_message(client):
    request_data = dict(
        recipient_ids=[2],
        from_user=1,
        text="My message",
        attachments=[]
    )
    resp = client.post("/messages/", json=request_data)
    assert resp.status_code == 200
    assert resp.json['timestamp'] is not None


def test_missing_recipients(client):
    request_data = dict(
        recipient_ids=[],
        from_user=1,
        text="My message",
        attachments=[]
    )
    resp = client.post("/messages/", json=request_data)
    assert resp.status_code == 422


def test_self_send_not_allowed(client):
    request_data = dict(
        recipient_ids=[1],
        from_user=1,
        text="My message",
        attachments=[]
    )
    resp = client.post("/messages/", json=request_data)
    assert resp.status_code == 422


def test_missing_content(client):
    request_data = dict(
        recipient_ids=[2],
        from_user=1,
        text="",
        attachments=[]
    )
    resp = client.post("/messages/", json=request_data)
    assert resp.status_code == 422


def test_attachment_only(client):
    request_data = dict(
        recipient_ids=[2],
        from_user=1,
        text="",
        attachments=[{
            "type": "audio",
            "url": "https://audiosomthing"
        }]
    )
    resp = client.post("/messages/", json=request_data)
    assert resp.status_code == 200


def test_invalid_attachment_type(client):
    request_data = dict(
        recipient_ids=[2],
        from_user=1,
        text="",
        attachments=[{
            "type": "something unsupported",
            "url": "https://audiosomthing"
        }]
    )
    resp = client.post("/messages/", json=request_data)
    assert resp.status_code == 422


def test_malformed_attachment_missing_url(client):
    request_data = dict(
        recipient_ids=[2],
        from_user=1,
        text="",
        attachments=[{
            "type": "audio",
            "url": ""
        }]
    )
    resp = client.post("/messages/", json=request_data)
    assert resp.status_code == 422


def test_malformed_attachment_missing_field(client):
    request_data = dict(
        recipient_ids=[2],
        from_user=1,
        text="",
        attachments=[{
            "type": "audio"
        }]
    )
    resp = client.post("/messages/", json=request_data)
    assert resp.status_code == 422


def test_missing_sender(client):
    request_data = dict(
        recipient_ids=[2],
        text="",
        attachments=[]
    )
    resp = client.post("/messages/", json=request_data)
    assert resp.status_code == 422


def test_query_missing_users(client):
    request_data = dict(
        user_ids=[]
    )
    resp = client.post("/messages/query", json=request_data)
    assert resp.status_code == 422


def test_query_since_user(client):
    request_data = dict(
        user_ids=[1]
    )
    resp = client.post("/messages/query", json=request_data)
    assert resp.status_code == 422


def test_query_multiple_users(client):
    request_data = dict(
        user_ids=[1, 2]
    )
    resp = client.post("/messages/query", json=request_data)
    assert resp.status_code == 200
