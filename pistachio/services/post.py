from datetime import datetime
from hashlib import md5

from pistachio.models import Post, User
from pistachio.services.s3 import S3Storage
from pistachio.services.schema import PostSchema
from pistachio.services.session_manager import SessionManagerBase

post_schema = PostSchema()


def generate_file_name(original_filename, ext="pdf"):
    filename_hash = md5(original_filename.encode()).hexdigest()
    timestamp = int(datetime.utcnow().timestamp())
    return f"{filename_hash}_{timestamp}.{ext}"


def create_post(
    user_id, file_name: str, file_obj, description: str, sm: SessionManagerBase
) -> dict:
    file_name = generate_file_name(file_name)
    S3Storage().write(file_name, file_obj)
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
