from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import requests
from flask import current_app


def encode_token(payload, algorithm="HS256", headers=None):
    return jwt.encode(
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
    return jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=[algorithm])


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
