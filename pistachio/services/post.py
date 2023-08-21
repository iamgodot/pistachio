from pistachio.models import Attachment, Post, User
from pistachio.services.schema import PostSchema
from pistachio.services.session_manager import SessionManagerBase

post_schema = PostSchema()


def create_post(
    user_id, file_name: str, file_url: str, description: str, sm: SessionManagerBase
) -> dict:
    with sm:
        user = sm.query.get(User, id=user_id)
        attachment = Attachment(name=file_name, url=file_url)
        post = Post(user=user, attachment=attachment, description=description)
        sm.query.add(attachment)
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
