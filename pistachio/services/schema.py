from marshmallow.fields import DateTime, Field, Int, Nested, Str

from pistachio.extensions import ma


class UserSchema(ma.Schema):
    id = Int()
    email = Str()
    username = Str()
    nickname = Str()
    avatar = Str()
    bio = Str()


class AttachmentSchema(ma.Schema):
    id = Int()
    name = Str()
    url = Str()


class PostSchema(ma.Schema):
    id = Int()
    user = Nested(UserSchema, data_key="author")
    attachment = Nested(AttachmentSchema)
    created_at = DateTime("%Y-%m-%d")
    updated_at = DateTime("%Y-%m-%d")
    description = Str()
