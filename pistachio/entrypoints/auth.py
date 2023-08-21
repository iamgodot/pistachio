"""
API for authentication and user management.
"""
from logging import getLogger

from apifairy import body, response
from flask import Blueprint, request
from marshmallow.fields import Str

from pistachio.decorators import authenticate
from pistachio.extensions import ma
from pistachio.services.auth import (
    AuthorizationFailed,
    InvalidCredential,
    UsernameTaken,
    UserNotFound,
    delete_user_by_id,
    generate_user_token,
    get_user_by_id,
    login_user,
    login_user_via_github,
    register_github_user,
    register_user,
    update_user_by_id,
)
from pistachio.services.schema import UserSchema as UserResponseSchema
from pistachio.services.session_manager import SessionManager

LOGGER = getLogger(__name__)
bp = Blueprint("auth", __name__)


class RegisterPayloadSchema(ma.Schema):
    nickname = Str()
    email = Str(required=True)
    password = Str(required=True)


@bp.post("/register")
@body(RegisterPayloadSchema)
@response(UserResponseSchema)
def register(payload):
    if not payload.get("email") or not payload.get("password"):
        return {"error": "Invalid payload"}, 400
    try:
        # FIXME: prevent email like foo@github.com
        user = register_user(**{**payload, "sm": SessionManager()})
        return user, 201
    except UsernameTaken as e:
        return {"error": str(e)}, 400


class LoginPayloadSchema(ma.Schema):
    email = Str()
    password = Str()
    type = Str(metadata={"description": "`github` for GitHub OAuth"})
    github_code = Str(metadata={"description": "code from GitHub OAuth code flow"})


class LoginResponseSchema(ma.Schema):
    access_token = Str()
    refresh_token = Str()


@bp.post("/login")
@body(LoginPayloadSchema)
@response(LoginResponseSchema)
def login(payload):
    LOGGER.debug("Payload: %s", payload)
    if payload.get("type") == "github":
        if not payload.get("github_code"):
            return {"error": "Invalid payload"}, 400
        try:
            gh_user_info = login_user_via_github(payload["github_code"])
            user = register_github_user(
                gh_user_info["login"],
                SessionManager(),
                avatar=gh_user_info["avatar_url"],
            )
        except (AuthorizationFailed, UsernameTaken) as e:
            return {"error": str(e)}, 400
    else:
        if not payload.get("email") or not payload.get("password"):
            return {"error": "Invalid payload"}, 400
        try:
            user = login_user(**{**payload, "sm": SessionManager()})
        except (UserNotFound, InvalidCredential) as e:
            return {"error": str(e)}, 400
    return {
        "access_token": generate_user_token(user["id"]),
        "refresh_token": generate_user_token(user["id"], refresh=True),
    }


@bp.get("/user")
@authenticate
@response(UserResponseSchema)
def get_current_user(user_id):
    try:
        return get_user_by_id(user_id, SessionManager())
    except UserNotFound as e:
        return {"error": str(e)}, 401


@bp.patch("/user")
@authenticate
@response(UserResponseSchema)
def update_current_user(user_id):
    """Update personal info of current user."""
    payload = request.get_json()
    if not payload.get("nickname") and not payload.get("bio"):
        return {"error": "Invalid payload"}, 400
    try:
        return update_user_by_id(user_id, SessionManager(), **payload)
    except UserNotFound as e:
        return {"error": str(e)}, 400


@bp.get("/users/<int:uid>")
@authenticate
@response(UserResponseSchema)
def get_user(uid, user_id):
    try:
        return get_user_by_id(uid, SessionManager())
    except UserNotFound as e:
        return {"error": str(e)}, 400


@bp.delete("/users/<int:uid>")
@authenticate
# FIXME: user should only be able to delete itself
def delete_user(uid, user_id):
    try:
        delete_user_by_id(uid, SessionManager())
    except UserNotFound as e:
        return {"error": str(e)}, 400
    return {}, 204
