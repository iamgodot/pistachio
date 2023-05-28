from logging import getLogger

import requests
from flask import Blueprint, g, request

from pistachio.decorators import authenticate
from pistachio.extensions import db
from pistachio.models.user import User
from pistachio.services.auth import (
    generate_user_token,
    get_gh_access_token,
    get_gh_user_info,
)

LOGGER = getLogger(__name__)
bp = Blueprint("auth", __name__)


def hash(s):
    from hashlib import md5

    return md5(s.encode()).hexdigest()


@bp.post("/register")
def register():
    try:
        payload = request.get_json()
        user = User(
            name=payload["name"],
            nickname=payload["nickname"],
            password_hash=hash(payload["password"]),
            description=payload["description"],
        )
        db.session.add(user)
        db.session.commit()
        return {"id": user.id, "name": user.name}, 201
    except Exception as e:
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
    try:
        payload = request.get_json()
        LOGGER.debug("Payload: %s", payload)
        if payload.get("type") == "github":
            try:
                gh_token = get_gh_access_token(payload["github_code"])
                LOGGER.debug("GitHub token: %s", gh_token)
                gh_user_info = get_gh_user_info(gh_token)
                gh_username = gh_user_info["login"]
                LOGGER.debug("GitHub username: %s", gh_username)
                if not (
                    user := db.session.execute(
                        db.select(User).filter_by(name=gh_username)
                    ).scalar()
                ):
                    print(user)
                    user = User(name=gh_username)
                    db.session.add(user)
                    db.session.commit()
            except requests.HTTPError:
                return {"error": "Failed to authorize by GitHub"}, 400
        else:
            user = db.session.execute(
                db.select(User).filter_by(name=payload["username"])
            ).scalar()
            if not user:
                return {"error": "User not found"}, 400
            elif hash(payload["password"]) != user.password_hash:
                return {"error": "Invalid password"}, 400
        return {
            "access_token": generate_user_token(user.id),
            "refresh_token": generate_user_token(user.id, refresh=True),
        }
    except Exception as e:
        return {"error": str(e)}, 400


@bp.get("/user")
@authenticate
def get_current_user():
    try:
        user = g.current_user
        return {
            "id": user.id,
            "name": user.name,
            "nickname": user.nickname,
            "description": user.description,
        }
    except Exception as e:
        return {"error": str(e)}, 400


@bp.get("/users/<int:user_id>")
def get_user(user_id):
    user = db.session.execute(db.select(User).filter_by(id=user_id)).scalar_one()
    if user:
        return {
            "id": user.id,
            "name": user.name,
            "nickname": user.nickname,
            "description": user.description,
        }
    else:
        return {"error": "No user found"}, 404


@bp.patch("/users/<int:user_id>")
def update_user(user_id):
    try:
        payload = request.get_json()
        user = db.session.execute(db.select(User).filter_by(id=user_id)).scalar_one()
        if not user:
            return {"error": "No user found"}, 404
        # from sqlalchemy import update
        # stmt = update(User).where(User.id == user_id).values(**payload)
        # db.session.execute(stmt)
        for k, v in payload.items():
            setattr(user, k, v)
        db.session.commit()
        return {
            "id": user.id,
            "name": user.name,
            "nickname": user.nickname,
            "description": user.description,
        }
    except Exception as e:
        return {"error": str(e)}, 400
