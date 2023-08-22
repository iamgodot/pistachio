from datetime import datetime
from hashlib import md5
from logging import getLogger

from boto3.session import Session
from botocore.exceptions import ClientError
from flask import current_app

from pistachio.models import Attachment, Post, User
from pistachio.services.schema import PostSchema
from pistachio.services.session_manager import SessionManagerBase

LOGGER = getLogger(__name__)
post_schema = PostSchema()


def create_post(
    user_id, file_name: str, description: str, sm: SessionManagerBase
) -> dict:
    with sm:
        user = sm.query.get(User, id=user_id)
        post = Post(user=user, file_name=file_name, description=description)
        sm.query.add(post)
        sm.commit()
        return post_schema.dump(post)


def get_posts(sm: SessionManagerBase) -> list:
    with sm:
        # TODO: sort desc
        posts = sm.query.list(Post)
        return [post_schema.dump(post) for post in posts]


def get_post_by_id(post_id, sm: SessionManagerBase) -> dict:
    with sm:
        post = sm.query.get(Post, id=post_id)
        return post_schema.dump(post)


def delete_post_by_id(post_id, sm: SessionManagerBase):
    with sm:
        sm.query.delete(Post, id=post_id)
        sm.commit()


def generate_file_name(original_filename, ext="pdf"):
    filename_hash = md5(original_filename.encode()).hexdigest()
    timestamp = int(datetime.utcnow().timestamp())
    return f"{filename_hash}_{timestamp}.{ext}"


def get_s3_client():
    config = current_app.config
    session = Session(
        aws_access_key_id=config["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=config["AWS_SECRET_ACCESS_KEY"],
        region_name=config["AWS_REGION_NAME"],
    )
    return session.client("s3")


def upload_to_s3(name, file_obj):
    file_name = generate_file_name(name)
    get_s3_client().upload_fileobj(
        file_obj, current_app.config["S3_BUCKET_NAME"], file_name
    )


def get_file_url_from_s3(name, expiration=3600) -> str | None:
    try:
        response = get_s3_client().generate_presigned_url(
            "get_object",
            Params={"Bucket": current_app.config["S3_BUCKET_NAME"], "Key": name},
            ExpiresIn=expiration,
        )
        return response
    except ClientError as e:
        LOGGER.exception(e)
