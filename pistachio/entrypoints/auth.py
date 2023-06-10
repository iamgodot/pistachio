from logging import getLogger

from flask import Blueprint, request

from pistachio.decorators import authenticate
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
    register_user,
    update_user_by_id,
)
from pistachio.services.session_manager import session_manager

LOGGER = getLogger(__name__)
bp = Blueprint("auth", __name__)


@bp.post("/register")
def register():
    payload = request.get_json()
    if (
        not payload.get("username")
        or not payload.get("email")
        or not payload.get("password")
    ):
        return {"error": "Invalid payload"}, 400
    try:
        user = register_user(**{**payload, "sm": session_manager})
        return user, 201
    except UsernameTaken as e:
        return {"error": str(e)}, 400


@bp.post("/login")
def login():
    """Login user with authorization token.

    Params:
        type: `github` or default to use username/password.
        github_code: for GitHub authorization.
    Returns:
        access_token: a JWT token with expiration.
        refresh_token: another JWT token.
    """
    payload = request.get_json()
    LOGGER.debug("Payload: %s", payload)
    if payload.get("type") == "github":
        if not payload.get("github_code"):
            return {"error": "Invalid payload"}, 400
        try:
            gh_user_info = login_user_via_github(payload["github_code"])
        except AuthorizationFailed as e:
            return {"error": str(e)}, 400
        # FIXME: gh username may conflict with existed user
        # Remove register logic here thus require another api call
        # NOTE: email might be None if one sets email address to private
        user = register_user(
            gh_user_info["login"], gh_user_info["email"] or "", "", session_manager
        )
    else:
        if not payload.get("username") or not payload.get("password"):
            return {"error": "Invalid payload"}, 400
        try:
            user = login_user(**{**payload, "sm": session_manager})
        except (UserNotFound, InvalidCredential) as e:
            return {"error": str(e)}, 400
    return {
        "access_token": generate_user_token(user["id"]),
        "refresh_token": generate_user_token(user["id"], refresh=True),
    }


@bp.get("/user")
@authenticate
def get_current_user(user_id):
    try:
        return get_user_by_id(user_id, session_manager)
    except UserNotFound as e:
        return {"error": str(e)}, 401


@bp.get("/users/<int:uid>")
@authenticate
def get_user(uid, user_id):
    try:
        get_user_by_id(user_id, session_manager)
    except UserNotFound as e:
        return {"error": str(e)}, 401
    try:
        return get_user_by_id(uid, session_manager)
    except UserNotFound as e:
        return {"error": str(e)}, 400


@bp.patch("/users/<int:uid>")
@authenticate
def update_user(uid, user_id):
    payload = request.get_json()
    if not payload.get("nickname") and not payload.get("bio"):
        return {"error": "Invalid payload"}, 400
    try:
        get_user_by_id(user_id, session_manager)
    except UserNotFound as e:
        return {"error": str(e)}, 401
    try:
        update_user_by_id(uid, session_manager, **payload)
    except UserNotFound as e:
        return {"error": str(e)}, 400
    return {"id": uid}, 200


@bp.delete("/users/<int:uid>")
@authenticate
def delete_user(uid, user_id):
    try:
        get_user_by_id(user_id, session_manager)
    except UserNotFound as e:
        return {"error": str(e)}, 401
    try:
        delete_user_by_id(uid, session_manager)
    except UserNotFound as e:
        return {"error": str(e)}, 400
    return {}, 204
