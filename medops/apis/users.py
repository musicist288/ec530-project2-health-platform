"""
    This module defines the blueprint for the devices API that can be integrated
    into a Flask app. It is intentionally declared separately so it is up to the
    operations team whether they want to host this API separately or in
    conjunction with another set of APIs.
"""
from datetime import date
from flask import (
    Blueprint,
    request,
    jsonify,
)

from .common import error_response
from .. import models

USERS_API_BLUEPRINT = Blueprint("users", __name__)

class UserEndpoint:

    @staticmethod
    def create():
        data = request.json
        errors = []
        if 'user_id' in data:
            errors.append("Do not provide a user id when creating a new user.")

        required_fields = [
            ("dob", lambda x: date.fromisoformat(x)),
            ("first_name", lambda x: str(x)),
            ("last_name", lambda x: str(x)),
        ]

        kwargs = {}
        for field, func in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
            else:
                try:
                    value = func(data[field])
                    kwargs[field] = value
                except Exception as err:
                    errors.append(f"Error creating field: {str(err)}")

        if "role_ids" not in data:
            errors.append("Missing required field: role_ids")
        else:
            role_ids = data['role_ids']
            kwargs['roles'] = roles = []
            for rid in role_ids:
                role = models.get_storage("users").user_roles.get(rid)
                if not role:
                    errors.append(f"Role does not exist with id: {rid}")
                    break
                else:
                    roles.append(role)

        if errors:
            return error_response(errors)
        else:
            user = models.User(**kwargs)
            user = models.get_storage("users").users.create(user)
            return jsonify(user=user.to_json())

    @staticmethod
    def get(user_id):
        """Stuff"""
        user = models.get_storage("users").users.get(user_id)
        errors = []
        if not user:
            errors.append(f"User {user_id} does not exist.")
            return error_response(errors=errors, status_code=404)
        else:
            return jsonify(user=user.to_json())

    @staticmethod
    def update(user_id):
        user = models.get_storage("users").users.get(user_id)
        patch_data = request.json

        errors = []
        if not user:
            errors.append(f"User {user_id} does not exist.")
            return error_response(errors=errors, status_code=404)

        editable = ["first_name", "last_name"]
        for field in editable:
            current = getattr(user, field)
            value = patch_data.get(field, current)
            setattr(user, field, value)

        if "dob" in patch_data:
            try:
                user.dob = date.fromisoformat(patch_data['dob'])
            except ValueError:
                errors.append(f"Invalid date string: {patch_data['dob']}")

        role_ids = patch_data['role_ids']
        roles = []
        for rid in role_ids:
            role = models.get_storage("users").user_roles.get(rid)
            if not role:
                errors.append(f"Role does not exist with id: {rid}")
                break
            else:
                roles.append(role)

        user.roles = roles

        if errors:
            return error_response(errors=errors)

        user = models.get_storage("users").users.update(user)
        return jsonify(user=user.to_json())

    @staticmethod
    def delete(user_id):
        models.get_storage("users").users.delete(user_id)
        return "", 201


class UserRoleEndpoint:

    @staticmethod
    def create():
        name = request.json.get("role_name", "")
        errors = []
        if "role_name" not in request.json:
            errors.append("Missing required field: role_name")

        if errors:
            return error_response(errors=errors)

        role = models.UserRole(role_name=name)
        role = models.get_storage("users").user_roles.create(role)
        return jsonify(user_role=role.to_json())

    @staticmethod
    def get(role_id):
        role = models.get_storage("users").user_roles.get(role_id)
        if not role:
            return error_response(
                errors=[f"User role does not exist with id: {role_id}"],
                status_code=404)

        return jsonify(user_role=role.to_json())

    @staticmethod
    def update(role_id):
        role = models.get_storage("users").user_roles.get(role_id)
        errors = []
        if not role:
            errors.append(f"User role does not exist with id: {role_id}")
            return error_response(errors=errors, status_code=404)

        name = request.json.get("role_name", "").strip()
        if not name:
            errors.append("Missing required field: role_name")

        if errors:
            return error_response(errors=errors)

        role.role_name = name
        role = models.get_storage("users").user_roles.update(role)
        return jsonify(user_role=role.to_json())


@USERS_API_BLUEPRINT.route("", methods=["POST"])
def user_create():
    return UserEndpoint.create()


@USERS_API_BLUEPRINT.route("/<int:user_id>", methods=["GET", "POST", "DELETE"])
def user(user_id: int):
    if request.method == "GET":
        return UserEndpoint.get(user_id)

    if request.method == "POST":
        return UserEndpoint.update(user_id)

    if request.method == "DELETE":
        return UserEndpoint.delete(user_id)

    return "", 501


@USERS_API_BLUEPRINT.route("/roles/<int:role_id>", methods=["GET", "POST"])
def user_role(role_id: int):
    if request.method == "GET":
        return UserRoleEndpoint.get(role_id)

    if request.method == "POST":
        return UserRoleEndpoint.update(role_id)

    return "", 501


@USERS_API_BLUEPRINT.route("/roles", methods=["POST"])
def user_role_create():
    return UserRoleEndpoint.create()