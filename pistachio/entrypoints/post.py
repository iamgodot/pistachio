from logging import getLogger

from apifairy import body, response
from flask import Blueprint, request
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
from pistachio.services.schema import UserSchema
from pistachio.services.session_manager import SessionManager

LOGGER = getLogger(__name__)
bp = Blueprint("post", __name__)


class PostSummaryResponseSchema(ma.Schema):
    summary = Str()


class PostResponseSchema(ma.Schema):
    id = Int()
    author = Nested(UserSchema)
    file_url = Str()
    created_at = Str()
    updated_at = Str()
    description = Str()


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

    # @pre_dump
    # def get_file_name(self, data, **kwargs):
    #     if not (file_name := data["file"].filename):
    #         raise ValidationError("File name required")
    #     data["file_name"] = secure_filename(file_name)
    #     return data


@bp.post("/posts")
@authenticate
@body(CreatePostPayloadSchema)
@response(PostResponseSchema, 201)
def create_post_(payload, user_id):
    # TODO: get from payload
    file = request.files["file"]
    file_name = secure_filename(file.filename)
    LOGGER.debug("File: %s", file)
    LOGGER.debug("File name: %s", file_name)
    description = request.form["description"]
    post = create_post(user_id, file_name, file, description, SessionManager())
    return post, 201


@bp.get("/posts")
@authenticate
def get_posts_(user_id):
    posts = get_posts(SessionManager())
    schema = PostResponseSchema()
    return [schema.dump(post) for post in posts]


@bp.get("/posts/<int:post_id>")
@authenticate
@response(PostResponseSchema)
def get_post(post_id, user_id):
    post = get_post_by_id(post_id, SessionManager())
    return post


@bp.delete("/posts/<int:post_id>")
@authenticate
def delete_post(post_id, user_id):
    delete_post_by_id(post_id, SessionManager())
    return {}, 204
