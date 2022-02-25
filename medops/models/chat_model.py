"""
    This module defines the modules and APIs for managing
    chat messages in the MedOps infrastructure.
"""

from typing import Optional

from dataclasses import dataclass, field
from datetime import datetime


SUPPORTED_ATTACHMENT_TYPES = [
    "video",
    "audio",
    "image",
    "file"
]


@dataclass
class MessageAttachmentV1:
    """Message Attachment, Version 1

    Parameters
    ----------
    type : str
        The type of attachment. Must be one of: video, audio, image, file

    url : str
        The URL of the attachment.

    attachment_version : int
        Don't touch this.
    """
    type: str
    url: str
    attachment_version = 1


@dataclass
class MessageV1:
    """Chat message, Version 1

    Parameters
    ----------
    timestamp : str
        The timestamp when the message was logged. ISO-8601 format.

    from_user : int
        The id of the user who sent the message.

    text : str
        The content of the message

    attachments : list
        A list of attachments sent with the message.

    messsage_version : int
        A field to map the version to this class type when deserializing
        data. Don't overwrite it unless you want to have a bad time.`
    """

    timestamp: str
    from_user: int
    text: str
    attachments: list[MessageAttachmentV1] = field(default_factory=lambda: [])
    message_version = 1

    def __post_init__(self):
        for attachment in self.attachments:
            if attachment.type not in SUPPORTED_ATTACHMENT_TYPES:
                raise ValueError(f"Unsupported attachement type: {attachment.type}")


def _get_chat_id(user_ids: set[int]) -> str:
    """Get a hashed chat ID for a list of recipients.

    Parameters
    ----------
    user_ids : set[int]
        The set (i.e. order doesn't matter) of users participating in the chat.

    Returns
    -------
    A unique identifier for the list of members in the chat. This is the key
    that is used to log the chat in the database.
    """
    pass


def query_latest_messages(
        user_ids: list[int],
        until: Optional[datetime] = None,
        limit=10) -> list[MessageV1]:
    """Retrieve the last `limit` number of messages until a specified time.

    Parameters
    ----------
    user_ids : list[int]
        The users

    until : Optional[datetime]
        The date until which to consider messages. If this is none, this
        funciton will return the last `limit` messages sent in the chat.
        If set to a datetime, it will return the last `limit` messages
        before the timestamp provided.

    limit : int
        The maximum number of messages to return. Must be > 0.

    Returns
    -------
    A list of messages ordered by timestamp from host historical to most
    recent.
    """


def query_time_range(
        user_ids: list[int],
        since: Optional[datetime] = None,
        until: Optional[datetime] = None) -> list[MessageV1]:
    """Query for chat messages within a date range.

    Parameters
    ----------
    chat_id : str
        The id of the chat to query.

    since : Optional[datetime]
        The most historcal datetime from which to consider messages. If set to None,
        it will query from the beginning of time.

    until : Optional[datetime]
        The most recent datetime to include messages from. If set to None,
        this will

    Returns
    -------
    A list of messages ordered from most historical to most recent.
    """


def log_message(user_ids: list[int], message: MessageV1):
    """Log a message to the chat log.

    Parameters
    ----------
    chat_id: str
        The identifier of the chat to send the message to.
        See `get_chat_id`
    """
