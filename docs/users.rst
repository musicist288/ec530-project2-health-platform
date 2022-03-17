Users and User Roles
====================

The MedOps platform provides a generic system for managing users and user roles.
The user model is quite simple and each user can have one or more roles. One
thing that MedOps does not provide is any sense of authentication or
permissions management. You may choose to implement this system in your applications
but it there are no controls for such in user apis.

Users can only be assigned ot user roles taht exist, so make sure you
create them first. When a user's roles are updated, it's up to the underlying
storage utilities to update the persist those changes, taking care to both
add and remove roles as appropriate.

Make sure to check out :ref:`rest-api-documentation`.

User Models
-----------
.. currentmodule:: medops.models.user_models

.. autoclass:: User

|

.. autoclass:: UserModel

|

.. autoclass:: UserRole

|

.. autoclass:: UserRoleModel

|

.. autoclass:: UserStorage

|

.. autoclass:: UserModelStorage
    :members:

|

.. autoclass:: UserRoleModelStorage
    :members:
