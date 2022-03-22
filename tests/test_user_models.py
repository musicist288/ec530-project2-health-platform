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
    cleanup()

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


def test_update_user_roles(user_storage):
    admin = UserRole(role_name="Admin")
    patient = UserRole(role_name="Patient")

    # Create the basline user and with admin roles.
    admin = user_storage.user_roles.create(admin)
    patient = user_storage.user_roles.create(patient)
    user = User(dob=date(year=1990, month=1, day=1),
                first_name="John",
                last_name="Doe",
                roles=[admin])
    user = user_storage.users.create(user)

    user.roles.append(patient)
    user_storage.users.update(user)
    user = user_storage.users.get(user.user_id)
    assert admin in user.roles
    assert patient in user.roles

    user.roles = []
    user_storage.users.update(user)
    user = user_storage.users.get(user.user_id)
    assert len(user.roles) == 0

    user.roles = [admin]
    user_storage.users.update(user)
    user = user_storage.users.get(user.user_id)
    assert admin in user.roles

    user.roles = [patient]
    user_storage.users.update(user)
    user = user_storage.users.get(user.user_id)
    assert admin not in user.roles
    assert patient in user.roles

def test_user_relationship_on_create(user_storage):
    doctor_role = UserRole(role_name="Doctor")
    patient_role = UserRole(role_name="Patient")
    doctor_role = user_storage.user_roles.create(doctor_role)
    patient_role = user_storage.user_roles.create(patient_role)

    doctor = User(dob=date(year=1990, month=1, day=1),
                  first_name="Doctor",
                  last_name="Doe",
                  roles=[doctor_role])
    doctor = user_storage.users.create(doctor)
    assert doctor.user_id is not None
    assert doctor.roles[0].role_id == doctor_role.role_id

    patient = User(dob=date(year=1990, month=1, day=1),
                   first_name="Patient",
                   last_name="Doe",
                   roles=[patient_role])

    patient.medical_staff.append(doctor)
    patient = user_storage.users.create(patient)
    assert len(patient.medical_staff) == 1

    doctor = user_storage.users.get(doctor.user_id)
    assert len(doctor.patients) == 1
    assert doctor.patients[0].user_id == patient.user_id


def test_user_relationships_on_update(user_storage):
    doctor_role = UserRole(role_name="Doctor")
    doctor_role = user_storage.user_roles.create(doctor_role)
    patient_role = UserRole(role_name="Patient")
    patient_role = user_storage.user_roles.create(patient_role)
    doctor = User(dob=date(year=1990, month=1, day=1),
                  first_name="Doctor",
                  last_name="Doe",
                  roles=[doctor_role])
    doctor = user_storage.users.create(doctor)
    patient = User(dob=date(year=1990, month=1, day=1),
                   first_name="Patient",
                   last_name="Doe",
                   roles=[patient_role])
    patient = user_storage.users.create(patient)
    doctor.patients.append(patient)
    doctor = user_storage.users.update(doctor)
    patient = user_storage.users.get(patient.user_id)
    assert len(patient.medical_staff) == 1
    assert patient.medical_staff[0].user_id == doctor.user_id

def test_remove_user_relationship(user_storage):
    doctor_role = UserRole(role_name="Doctor")
    doctor_role = user_storage.user_roles.create(doctor_role)
    patient_role = UserRole(role_name="Patient")
    patient_role = user_storage.user_roles.create(patient_role)
    doctor = User(dob=date(year=1990, month=1, day=1),
                  first_name="Doctor",
                  last_name="Doe",
                  roles=[doctor_role])
    doctor = user_storage.users.create(doctor)
    patient = User(dob=date(year=1990, month=1, day=1),
                   first_name="Patient",
                   last_name="Doe",
                   roles=[patient_role])
    patient = user_storage.users.create(patient)
    doctor.patients.append(patient)
    doctor = user_storage.users.update(doctor)
    patient = user_storage.users.get(patient.user_id)

    patient.medical_staff = []
    patient = user_storage.users.update(patient)

    # Make sure the relationship was removed and is gone on
    # both ends.
    patient = user_storage.users.get(patient.user_id)
    doctor = user_storage.users.get(doctor.user_id)
    assert not patient.medical_staff
    assert not doctor.patients

def create_user(name, roles, storage):
    user = User(dob=date(year=1990, month=1, day=1),
                first_name="Doctor_Patient_1",
                last_name="Doe",
                roles=roles)
    return storage.users.create(user)

def test_mix_n_match_relationships(user_storage):
    doctor_role = UserRole(role_name="Doctor")
    doctor_role = user_storage.user_roles.create(doctor_role)
    patient_role = UserRole(role_name="Patient")
    patient_role = user_storage.user_roles.create(patient_role)
    doctor_1 = create_user("Doctor_Patient_1", [doctor_role, patient_role], user_storage)
    doctor_2 = create_user("Doctor_Patient_2", [doctor_role, patient_role], user_storage)
    patient = create_user("Patient Only", [patient_role], user_storage)

    doctor_1, doctor_2, patient = user_storage.users.get([
        doctor_1.user_id,
        doctor_2.user_id,
        patient.user_id])
    assert doctor_1.user_id is not None
    assert doctor_2.user_id is not None
    assert patient.user_id is not None

    doctor_1.patients.append(patient)
    doctor_2.patients.append(patient)
    user_storage.users.update(doctor_1)
    user_storage.users.update(doctor_2)
    doctor_1, doctor_2, patient = user_storage.users.get([
        doctor_1.user_id,
        doctor_2.user_id,
        patient.user_id])

    assert len(patient.medical_staff) == 2
    assert {p.user_id for p in patient.medical_staff} == {doctor_1.user_id, doctor_2.user_id}

    doctor_1.patients.append(doctor_2)
    user_storage.users.update(doctor_1)
    doctor_1, doctor_2, patient = user_storage.users.get([
        doctor_1.user_id,
        doctor_2.user_id,
        patient.user_id])
    assert len(doctor_1.patients) == 2
    assert len(doctor_2.medical_staff) == 1

    # Deleting a user should delete all their relationships.
    user_storage.users.delete(patient.user_id)
    doctor_1, doctor_2, patient = user_storage.users.get([
        doctor_1.user_id,
        doctor_2.user_id,
        patient.user_id])

    assert patient is None
    assert len(doctor_1.patients) == 1
    assert len(doctor_2.patients) == 0
