"""
    This module implements the REST API for the chat module
    as a flask blueprint.
"""

from flask import (
    Blueprint,
    jsonify,
    request
)

from dataclasses import dataclass, field
from typing import Optional

from .common import error_response
from .. import models
from ..models import chat_model

MESSAGES_API_BLUEPRINT = Blueprint("messages", __name__)

@dataclass
class CreateMessageRequest:
    """A class representing the a request to send a messages
    """
    from_user: Optional[int] = None
    text: Optional[str] = None
    attachments: list[int] = field(default_factory=lambda: [])
    recipient_ids: list[int] = field(default_factory=lambda: [])


class MessageEndpoints:

    @staticmethod
    def post():
        req = CreateMessageRequest(**request.json)
        errors = []
        if not req.recipient_ids:
            errors.append("Must specificy at least one or more recipient.")

        if req.recipient_ids == [req.from_user]:
            errors.append("You can't send messages to yourself.")

        if not req.from_user:
            errors.append("Missing required field: from_user")

        if not req.text and not req.attachments:
            errors.append("Either text or an attachment is required.")

        # TODO: Validate from user and recipient ids exist.

        try:
            attachments = [chat_model.MessageAttachmentV1(**data) for data in req.attachments]
        except ValueError as err:
            errors.append(str(err))
        except TypeError:
            errors.append("Attachment is malformed.")

        if errors:
            return error_response(errors)

        message = chat_model.MessageV1(
            from_user=req.from_user,
            text=req.text or "",
            attachments=attachments,
        )
        models.get_storage("messages").log_message(req.recipient_ids, message)
        return jsonify(message.to_dict())


class MessagesQueryEndpoint:

    @staticmethod
    def post():
        pass


@MESSAGES_API_BLUEPRINT.route("/", methods=["POST"])
def message_route():
    if request.method == "POST":
        return MessageEndpoints.post()

@MESSAGES_API_BLUEPRINT.route("/query", methods=["POST"])
def message_query_route():
    if request.method == "POST":
        return MessageEndpoints.post()

    return "Not implemented", 501
