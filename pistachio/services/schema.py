from marshmallow.fields import DateTime, Int, Nested, Str

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
    file_name = Str()
    file_url = Str()
    created_at = DateTime("%Y-%m-%d %H:%M")
    updated_at = DateTime("%Y-%m-%d %H:%M")
    description = Str()
