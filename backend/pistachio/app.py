from datetime import datetime, timedelta, timezone
from hashlib import md5
from os import environ
from uuid import uuid4

import jwt
import requests
from flask import Blueprint, Flask, request
from flask_sqlalchemy import SQLAlchemy

from .config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/prod.db"

db = SQLAlchemy()
db.init_app(app)
bp = Blueprint("core", __name__)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    nickname = db.Column(db.String(30), nullable=False, default="")
    password_hash = db.Column(db.String(16), nullable=False, default="")
    description = db.Column(db.Text, nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref=db.backref("posts", lazy=True))
    filename = db.Column(db.String(30), nullable=False)
    download_url = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


if not environ.get("TEST", None):
    with app.app_context():
        db.create_all()


def hash(s):
    return md5(s.encode()).hexdigest()


@app.get("/")
def index():
    return "<html><h2>Welcome to Pistachio</h2></html>"


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


def encode_token(payload, algorithm="HS256", headers=None):
    return jwt.encode(
        payload, app.config["JWT_SECRET"], algorithm=algorithm, headers=headers
    )


def get_jti():
    return uuid4().hex


def get_exp(refresh=False):
    return datetime.now(tz=timezone.utc) + timedelta(
        seconds=app.config["ACCESS_TOKEN_TTL"]
        if not refresh
        else app.config["REFRESH_TOKEN_TTL"]
    )


def generate_user_token(sub, jti=None, exp=None, refresh=False):
    if not jti:
        jti = get_jti()
    if not exp:
        exp = get_exp(refresh)
    return encode_token({"sub": sub, "jti": jti, "exp": exp, "refresh": refresh})


def get_gh_access_token(code):
    resp = requests.post(
        "https://github.com/login/oauth/access_token",
        json={
            "client_id": app.config["GITHUB_CLIENT_ID"],
            "client_secret": app.config["GITHUB_CLIENT_SECRET"],
            "code": code,
        },
    )
    return resp.json()["access_token"]


def get_gh_user_info(token):
    return requests.get(
        "https://api.github.com/user",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
        },
    )


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
        if payload.get("type") == "github":
            try:
                gh_token = get_gh_access_token(payload["github_code"])
                gh_user_info = get_gh_user_info(gh_token)
                gh_username = gh_user_info["login"]
                if not (
                    user := db.session.execute(
                        db.select(User).filter_by(name=gh_username)
                    ).scalar()
                ):
                    user = User(name=gh_username)
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


@bp.post("/posts")
def create_post():
    try:
        payload = request.get_json()
        post = Post(
            user_id=payload["user_id"],
            filename=payload["filename"],
            download_url="",
            description=payload["description"],
        )
        db.session.add(post)
        db.session.commit()
        return {
            "id": post.id,
            "filename": post.filename,
            "download_url": post.download_url,
            "description": post.description,
        }
    except Exception as e:
        return {"error": str(e)}, 400


@bp.get("/posts")
def get_posts():
    posts = db.session.execute(db.select(Post)).scalars()
    return [
        {
            "id": post.id,
            "filename": post.filename,
            "download_url": post.download_url,
            "description": post.description,
        }
        for post in posts
    ]


@bp.get("/posts/<int:post_id>")
def get_post(post_id):
    post = db.session.execute(db.select(Post).filter_by(id=post_id)).scalar_one()
    if post:
        return {
            "id": post.id,
            "filename": post.filename,
            "download_url": post.download_url,
            "description": post.description,
        }
    else:
        return {"error": "No post found"}, 404


@bp.delete("/posts/<int:post_id>")
def foo(post_id):
    post = db.session.execute(db.select(Post).filter_by(id=post_id)).scalar_one()
    if post:
        db.session.delete(post)
        db.session.commit()
        return {}, 204
    return {"error": "No post found"}, 404


app.register_blueprint(bp, url_prefix="/v1")
