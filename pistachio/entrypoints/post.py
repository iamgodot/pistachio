from logging import getLogger
from os.path import join

from apifairy import body, response
from flask import Blueprint, current_app, request
from marshmallow.fields import Field, Int, Nested, Str
from werkzeug.utils import secure_filename

from pistachio.decorators import authenticate
from pistachio.extensions import ma
from pistachio.services.chat_pdf import summarize
from pistachio.services.post import (
    create_post,
    delete_post_by_id,
    get_post_by_id,
    get_posts,
)
from pistachio.services.schema import UserSchema as UserResponseSchema
from pistachio.services.session_manager import SessionManager

LOGGER = getLogger(__name__)
bp = Blueprint("post", __name__)


class PostSummaryResponseSchema(ma.Schema):
    summary = Str()


@bp.get("/posts/<int:post_id>/summary")
@response(PostSummaryResponseSchema)
def get_post_summary(post_id):
    post = get_post_by_id(post_id, SessionManager())
    file_url = post["attachment"]["url"]
    summary = summarize(file_url)
    return {"summary": summary}


class CreatePostPayloadSchema(ma.Schema):
    description = Str()
    file = Field(metadata={"type": "string", "format": "byte"})


class PostResponseSchema(ma.Schema):
    id = Int()
    author = Nested(UserResponseSchema)
    description = Str()
    file_url = Str()
    created_at = Str()


@bp.post("/posts")
@authenticate
@body(CreatePostPayloadSchema)
@response(PostResponseSchema, 201)
def create_post_(payload, user_id):
    file = request.files["file"]
    LOGGER.debug("File: %s", file)
    LOGGER.debug("File name: %s", file.filename)
    description = request.form["description"]
    file_name = secure_filename(file.filename or "")
    file_path = join(current_app.root_path, file_name)
    file.save(file_path)
    post = create_post(user_id, file_name, file_path, description, SessionManager())
    # TODO: define a hook in schema
    post["file_url"] = post["attachment"]["url"]
    return post, 201


@bp.get("/posts")
@authenticate
def get_posts_(user_id):
    posts = get_posts(SessionManager())
    for post in posts:
        post["file_url"] = post["attachment"]["url"]
    schema = PostResponseSchema()
    return [schema.dump(post) for post in posts]


@bp.get("/posts/<int:post_id>")
@authenticate
@response(PostResponseSchema)
def get_post(post_id, user_id):
    post = get_post_by_id(post_id, SessionManager())
    post["file_url"] = post["attachment"]["url"]
    return post


@bp.delete("/posts/<int:post_id>")
@authenticate
def delete_post(post_id, user_id):
    delete_post_by_id(post_id, SessionManager())
    return {}, 204
