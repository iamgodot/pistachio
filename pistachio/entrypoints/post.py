from logging import getLogger

from apifairy import body, response
from flask import Blueprint, request
from marshmallow import pre_dump
from marshmallow.fields import Field, Str
from werkzeug.utils import secure_filename

from pistachio.decorators import authenticate
from pistachio.extensions import ma
from pistachio.services.chat_pdf import summarize
from pistachio.services.post import (
    create_post,
    delete_post_by_id,
    generate_file_name,
    get_file_url_from_s3,
    get_post_by_id,
    get_posts,
    upload_to_s3,
)
from pistachio.services.schema import PostSchema
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


class PostResponseSchema(PostSchema):
    created_at = Str()
    updated_at = Str()

    @pre_dump
    def get_file_url(self, data, **kwargs):
        data["file_url"] = get_file_url_from_s3(data.pop("file_name"))
        return data


@bp.post("/posts")
@authenticate
@body(CreatePostPayloadSchema)
@response(PostResponseSchema, 201)
def create_post_(payload, user_id):
    file = request.files["file"]
    if not file.filename:
        return {"error": "Invalid file name"}, 400
    LOGGER.debug("File: %s", file)
    LOGGER.debug("File name: %s", file.filename)
    description = request.form["description"]
    file_name = generate_file_name(secure_filename(file.filename))
    upload_to_s3(file_name, file)
    post = create_post(user_id, file_name, description, SessionManager())
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
