from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import registry, relationship

from pistachio.models import Attachment, Post, User

metadata = MetaData()

user = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    # TODO: index
    Column("username", String(20), nullable=False),
    Column("password_hash", String(60), nullable=False),
    Column("nickname", String(50), nullable=False),
    Column("email", String(50), nullable=False),
    Column("avatar", String(100), nullable=False),
    Column("bio", Text, default=""),
    Column("created_at", DateTime, nullable=False, default=datetime.now),
)

follow = Table(
    "follow",
    metadata,
    # NOTE: recommandation practice, see above https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#setting-bi-directional-many-to-many
    Column("following_id", ForeignKey("user.id"), primary_key=True, nullable=False),
    Column("follower_id", ForeignKey("user.id"), primary_key=True, nullable=False),
)

post = Table(
    "post",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("file_name", String(47), nullable=False, default=""),
    Column("description", Text, nullable=False, default=""),
    Column("created_at", DateTime, nullable=False, default=datetime.now),
    Column("updated_at", DateTime, nullable=False, default=datetime.now),
    Column("user_id", ForeignKey("user.id")),
)

attachment = Table(
    "attachment",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(50), nullable=False),
    Column("url", String(100), nullable=False),
    Column("post_id", ForeignKey("post.id", ondelete="CASCADE")),
)

mapper_registry = registry()


def start_mappers():
    mapper_registry.map_imperatively(
        User,
        user,
        properties={
            "posts": relationship(Post, back_populates="user"),
            "followers": relationship(
                User,
                secondary=follow,
                primaryjoin=user.columns.id == follow.columns.following_id,
                secondaryjoin=user.columns.id == follow.columns.follower_id,
                back_populates="followings",
            ),
            "followings": relationship(
                User,
                secondary=follow,
                primaryjoin=user.columns.id == follow.columns.follower_id,
                secondaryjoin=user.columns.id == follow.columns.following_id,
                back_populates="followers",
            ),
        },
    )
    mapper_registry.map_imperatively(
        Post,
        post,
        properties={
            "user": relationship(User, back_populates="posts"),
            "attachment": relationship(
                Attachment,
                uselist=False,
                back_populates="post",
                cascade="all, delete-orphan",
                passive_deletes=True,
            ),
        },
    )
    mapper_registry.map_imperatively(
        Attachment,
        attachment,
        properties={
            "post": relationship(
                Post,
                uselist=False,
                back_populates="attachment",
            )
        },
    )
