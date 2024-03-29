from datetime import datetime, timedelta, timezone
from logging import getLogger
from uuid import uuid4

import requests
from flask import current_app
from jwt import decode, encode
from jwt.exceptions import PyJWTError
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from pistachio.models import User
from pistachio.services.schema import UserSchema
from pistachio.services.session_manager import SessionManagerBase
from pistachio.utils import verify_password

LOGGER = getLogger(__name__)
user_schema = UserSchema()


def encode_token(payload, algorithm="HS256", headers=None):
    return encode(
        payload, current_app.config["JWT_SECRET"], algorithm=algorithm, headers=headers
    )


def get_jti():
    return uuid4().hex


def get_exp(refresh=False):
    return datetime.now(tz=timezone.utc) + timedelta(
        seconds=current_app.config["ACCESS_TOKEN_TTL"]
        if not refresh
        else current_app.config["REFRESH_TOKEN_TTL"]
    )


def generate_user_token(sub, jti=None, exp=None, refresh=False):
    if not jti:
        jti = get_jti()
    if not exp:
        exp = get_exp(refresh)
    return encode_token({"sub": sub, "jti": jti, "exp": exp, "refresh": refresh})


def decode_token(token, algorithm="HS256"):
    try:
        return decode(token, current_app.config["JWT_SECRET"], algorithms=[algorithm])
    except PyJWTError as e:
        raise TokenDecodeException(str(e))


class TokenDecodeException(Exception):
    pass


def get_gh_access_token(code):
    resp = requests.post(
        "https://github.com/login/oauth/access_token",
        json={
            "client_id": current_app.config["GITHUB_CLIENT_ID"],
            "client_secret": current_app.config["GITHUB_CLIENT_SECRET"],
            "code": code,
        },
        headers={
            "Accept": "application/json",
        },
    )
    return resp.json()["access_token"]


def get_gh_user_info(token):
    return requests.get(
        "https://api.github.com/user",
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        },
    ).json()


class UsernameTaken(Exception):
    pass


class UserNotFound(Exception):
    pass


class InvalidCredential(Exception):
    pass


class AuthorizationFailed(Exception):
    pass


def register_user(email, password, sm: SessionManagerBase, **other_info) -> dict:
    user = User(email=email, password=password, **other_info)
    with sm:
        if sm.query.first(User, email=email) is not None:
            raise UsernameTaken(f"User already exists: {email}")
        sm.query.add(user)
        sm.commit()
        return user_schema.dump(user)


def login_user(email, password, sm: SessionManagerBase) -> dict:
    with sm:
        if not (user := sm.query.first(User, email=email)):
            raise UserNotFound(f"User not found: {email}")
        if verify_password(password, user.password_hash) is False:
            raise InvalidCredential(f"Wrong password for user: {email}")
        return user_schema.dump(user)


def register_github_user(username, sm: SessionManagerBase, **other_info) -> dict:
    """If username does not exist, register user with github as email."""
    with sm:
        if not (user := sm.query.first(User, username=username)):
            user = User(
                email=f"{username}@github.com",
                username=username,
                nickname=username,
                **other_info,
            )
            sm.query.add(user)
            sm.commit()
        return user_schema.dump(user)


def login_user_via_github(code) -> dict:
    """Return authenticated user info from GitHub.
        {
      "login": "octocat",
      "id": 1,
      "node_id": "MDQ6VXNlcjE=",
      "avatar_url": "https://github.com/images/error/octocat_happy.gif",
      "gravatar_id": "",
      "url": "https://api.github.com/users/octocat",
      "html_url": "https://github.com/octocat",
      "followers_url": "https://api.github.com/users/octocat/followers",
      "following_url": "https://api.github.com/users/octocat/following{/other_user}",
      "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
      "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
      "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
      "organizations_url": "https://api.github.com/users/octocat/orgs",
      "repos_url": "https://api.github.com/users/octocat/repos",
      "events_url": "https://api.github.com/users/octocat/events{/privacy}",
      "received_events_url": "https://api.github.com/users/octocat/received_events",
      "type": "User",
      "site_admin": false,
      "name": "monalisa octocat",
      "company": "GitHub",
      "blog": "https://github.com/blog",
      "location": "San Francisco",
      "email": "octocat@github.com",
      "hireable": false,
      "bio": "There once was...",
      "twitter_username": "monatheoctocat",
      "public_repos": 2,
      "public_gists": 1,
      "followers": 20,
      "following": 0,
      "created_at": "2008-01-14T04:33:35Z",
      "updated_at": "2008-01-14T04:33:35Z",
      "private_gists": 81,
      "total_private_repos": 100,
      "owned_private_repos": 100,
      "disk_usage": 10000,
      "collaborators": 8,
      "two_factor_authentication": true,
      "plan": {
        "name": "Medium",
        "space": 400,
        "private_repos": 20,
        "collaborators": 0
      }
    }
    """
    try:
        gh_token = get_gh_access_token(code)
        LOGGER.debug("GitHub token: %s", gh_token)
        gh_user_info = get_gh_user_info(gh_token)
        LOGGER.debug("GitHub userinfo: %s", gh_user_info)
        assert "login" in gh_user_info
        return gh_user_info
    except (requests.HTTPError, AssertionError, KeyError):
        raise AuthorizationFailed("Failed to authorize by GitHub")


def get_user_by_id(user_id, sm: SessionManagerBase) -> dict:
    with sm:
        try:
            user = sm.query.get(User, id=user_id)
        except (NoResultFound, MultipleResultsFound):
            raise UserNotFound(f"User {user_id} not found")
        return user_schema.dump(user)


def update_user_by_id(user_id, sm: SessionManagerBase, **params) -> dict:
    with sm:
        try:
            user = sm.query.get(User, id=user_id)
        except (NoResultFound, MultipleResultsFound):
            raise UserNotFound(f"User {user_id} not found")
        sm.query.update(User, params, id=user_id)
        sm.commit()
        return user_schema.dump(user)


def delete_user_by_id(user_id, sm: SessionManagerBase) -> None:
    with sm:
        try:
            sm.query.get(User, id=user_id)
        except (NoResultFound, MultipleResultsFound):
            raise UserNotFound(f"User {user_id} not found")
        sm.query.delete(User, id=user_id)
        sm.commit()
