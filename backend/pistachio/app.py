from datetime import datetime
from hashlib import md5
from os import environ

from flask import Blueprint, Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/prod.db"
db = SQLAlchemy()
db.init_app(app)
bp = Blueprint("core", __name__)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    nickname = db.Column(db.String(30), nullable=False)
    password_hash = db.Column(db.String(16), nullable=False)
    description = db.Column(db.Text, nullable=False)
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


@bp.post("/login")
def login():
    try:
        payload = request.get_json()
        user = db.session.execute(
            db.select(User).filter_by(name=payload["username"])
        ).scalar_one()
        if hash(payload["password"]) == user.password_hash:
            return {"id": user.id}
        else:
            return {"error": "Invalid password"}, 400
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
