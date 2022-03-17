import pytest
import atexit
import os
from datetime import date

from medops.models.user_models import (
    User,
    UserRole,
    UserStorage,
    UserRoleUserModel
)

FILENAME = "user_test.db"

def cleanup():
    if os.path.exists(FILENAME):
        os.unlink(FILENAME)

atexit.register(cleanup)

@pytest.fixture
def user_storage():
    user_storage = UserStorage(FILENAME)
    yield user_storage
    user_storage.deinit()

def test_create_user_role(user_storage):
    role = UserRole(role_name="Admin")
    role = user_storage.user_roles.create(role)
    assert role.role_id is not None
    created_role = user_storage.user_roles.get(role.role_id)
    assert role == created_role


def test_delete_user_role(user_storage):
    role = UserRole(role_name="Admin")
    role = user_storage.user_roles.create(role)
    assert role.role_id is not None
    deleted = user_storage.user_roles.delete(role.role_id)
    assert deleted

    retrieved = user_storage.user_roles.get(role.role_id)
    assert retrieved is None


def test_update_user_role(user_storage):
    role = UserRole(role_name="Admin")
    role = user_storage.user_roles.create(role)
    assert role.role_id is not None

    role.role_name = "Administrator"
    user_storage.user_roles.update(role)

    retrieved = user_storage.user_roles.get(role.role_id)
    assert retrieved.role_name == role.role_name
    assert retrieved.role_id == role.role_id


def test_create_user(user_storage):
    role = UserRole(role_name="Admin")
    role = user_storage.user_roles.create(role)

    dob = date(year=1990, month=12, day=15)
    user = User(dob=dob, first_name="John", last_name="Doe", roles=[role])
    created = user_storage.users.create(user)
    assert created.user_id is not None
    assert created.roles[0].role_id == role.role_id


def test_delete_user(user_storage):
    role = UserRole(role_name="Admin")
    role = user_storage.user_roles.create(role)

    user = User(dob=date(year=1990, month=1, day=1),
                first_name="John",
                last_name="Doe",
                roles=[role])
    created = user_storage.users.create(user)
    assert created.user_id is not None
    assert created.roles[0].role_id == role.role_id

    deleted = user_storage.users.delete(created.user_id)
    assert deleted
    user = user_storage.users.get(created.user_id)
    assert user is None

    remaining_roles = UserRoleUserModel.select().where(UserRoleUserModel.user_id == created.user_id).count()
    assert remaining_roles == 0

def test_update_user(user_storage):
    role = UserRole(role_name="Admin")
    role = user_storage.user_roles.create(role)

    user = User(dob=date(year=1990, month=1, day=1),
                first_name="John",
                last_name="Doe",
                roles=[role])
    created = user_storage.users.create(user)
    assert created.user_id is not None
    assert created.roles[0].role_id == role.role_id

    created.dob = date(year=1991, day=23, month=11)
    updated = user_storage.users.update(created)
    assert updated.dob == created.dob
    read = user_storage.users.get(updated.user_id)
    assert read.dob == updated.dob
