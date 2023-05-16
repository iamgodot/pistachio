from logging import getLogger

from flask import Blueprint, request
from pistachio.decorators import authenticate
from pistachio.extensions import db
from pistachio.models.post import Post

LOGGER = getLogger(__name__)
bp = Blueprint("post", __name__)


@bp.post("/posts")
@authenticate
def create_post():
    # NOTE: without this log line, I kept getting err_connection_reset, which according
    # to the doc means 413 response when dev serving.
    LOGGER.debug(request.files.getlist("file"))
    try:
        user_id = request.form.get("user_id")
        file = request.files.getlist("file")[0]
        LOGGER.debug("File name: %s", file.name)
        description = request.form.getlist("description")[0]
        post = Post(
            user_id=user_id,
            # file.name => 'file' as request.files[0]
            filename=file.filename,
            download_url="",
            description=description,
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
@authenticate
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
