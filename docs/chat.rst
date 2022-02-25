.. currentmodule:: medops.models.chat_model

Chat
----

The MedOps chat models allow users to send messages to one or more users.
Message logs are stored as documents in MongoDB collections. Each collection
represents a single message log between a unique set of participants. The set of
participants is what makes a message log unique and this contains all
identifying information needed to store and retrieve a chat log. The set of
participants MUST include the user who is sending the message and there must
be more than one user.

That the models and APIs provided by the chat module simply for logging messages
to the database. They do not provide any real-time or publishing mechanism to
send messages to participants when new messages come in, nor do they provide a
way to query what chats a particular user is participating in. That information
will be tracked in a SQL database.

.. code-block:: JSON

    {
        "_id": "<message_id>",
        "schema_version": "<schema version>",
        "timestamp": "<timestamp the message was sent, UTC>",
        "user_id": "<user who sent the message>",
        "text": "<content of the message>",
        "attachments": [
            {
                "type": "video",
                "url": ""
            },
            {
                "type": "audio",
                "url": ""
            },
            {
                "type": "image",
                "url": ""
            },
            {
                "type": "file",
                "url": ""
            }
        ]
    }


Retrieving Message Logs
^^^^^^^^^^^^^^^^^^^^^^^
See the :func:`query_time_range` and :func:`query_latest_messages` functions
for retrieving a chat log from the database.


Logging Messages
^^^^^^^^^^^^^^^^
To log messages to a chat, you simply need to construct a message and use the
:func:`log_message` API to send it.

.. code-block:: python

    from datetime import datetime
    import chat_model
    # Create the message
    user_ids = set([3, 4])
    message = chat_model.Message(timestamp=datetime.now(),
                                 from_user=3,
                                 text="Hello, World!",
                                 attachments=[])

    # Send the message to user 4
    chat_model.log_message(user_ids, message)

    # Send the same message to a group chat between users
    # 2, 3, and 4
    user_ids = set([2, 3, 4])
    chat_model.log_message(user_ids, message)


Attachments
^^^^^^^^^^^
Users can send attachments to one another. The chat model simply
logs the type of media attached and a URL to its location and thus
does not distinguish between attachments hosted on MedOps or
elsewhere. Currently, MedOps does not support hosting attachments,
so all attachments must be links to files hosted elsewhere.

The supported attachemnt types are:

- :code:`file`
- :code:`video`
- :code:`audio`
- :code:`image`


Model APIs
==========

.. autoclass:: MessageV1
    :members:

|

.. autoclass:: MessageAttachmentV1
    :members:

|

.. autofunction:: query_latest_messages

|

.. autofunction:: query_time_range

|

.. autofunction:: log_message
