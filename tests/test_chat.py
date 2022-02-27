from datetime import datetime
from unittest import mock
import pytest
from medops.models import chat_model

FAKE_CONN_STR = "my mongo connection"
FAKE_DB = "fake db"

@pytest.fixture
def message_store():
    chat_model.pymongo.MongoClient = mock.MagicMock()
    store = chat_model.MessageStore(FAKE_CONN_STR, FAKE_DB)
    yield store


def test_message_store_create(message_store):
    store = message_store
    assert isinstance(store, chat_model.MessageStore)
    assert chat_model.pymongo.MongoClient.call_count == 1
    assert chat_model.pymongo.MongoClient.call_args[0][0] == FAKE_CONN_STR


def test_log_message(message_store):
    message = chat_model.MessageV1(
        timestamp=datetime.now(),
        from_user=1,
        text="A message",
        attachments=[]
    )
    to_users = [1, 2, 3]
    expected_id = message_store._get_chat_id(to_users)
    message_store.log_message(to_users, message)
    assert message_store.database.__getitem__.call_count == 1
    assert message_store.database.__getitem__.call_args[0][0] == expected_id

    # Order shouldn't matter.
    to_users = [3, 1, 2]
    message_store.log_message(to_users, message)
    assert message_store.database.__getitem__.call_count == 2
    assert message_store.database.__getitem__.call_args[0][0] == expected_id

    # Allow implicite addition of from_user to user ids
    to_users.remove(message.from_user) # user ids no longer contains the sender
    # But sending should still work
    message_store.log_message(to_users, message)
    # Expect the same ID as before!
    assert message_store.database.__getitem__.call_count == 3
    assert message_store.database.__getitem__.call_args[0][0] == expected_id

    # Different users should be logged somewhere else
    to_users = [3, 4, 1, 2]
    expected_id = message_store._get_chat_id(to_users)
    message_store.log_message(to_users, message)
    assert message_store.database.__getitem__.call_count == 4
    assert message_store.database.__getitem__.call_args[0][0] == expected_id


def test_message_attachments():
    message = chat_model.MessageV1(
        timestamp=datetime.now(),
        from_user=1,
        text="My message",
        attachments=[chat_model.MessageAttachmentV1("video", "https://google.com")]
    )

    # Make sure all the data is preserved when serializing.
    msg_dict = message.to_dict()
    assert isinstance(msg_dict, dict)
    assert msg_dict['timestamp'] == message.timestamp
    assert msg_dict['from_user'] == message.from_user
    assert msg_dict['text'] == message.text
    assert isinstance(msg_dict['attachments'][0], dict)
    assert msg_dict['attachments'][0]['type'] == "video"
    assert msg_dict['attachments'][0]['url'] == "https://google.com"

    # Assert that instantiating an attachment with an invalid type fails.
    try:
        chat_model.MessageAttachmentV1(type="unknown_type", url="twitter.com")
        assert False
    except ValueError:
        pass
