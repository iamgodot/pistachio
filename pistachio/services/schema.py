from marshmallow import pre_dump
from marshmallow.fields import DateTime, Int, Nested, Str

from pistachio.extensions import ma
from pistachio.services.s3 import S3Storage


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
    file_url = Str()
    created_at = DateTime("%Y-%m-%d %H:%M")
    updated_at = DateTime("%Y-%m-%d %H:%M")
    description = Str()

    @pre_dump
    def get_file_url(self, data, **kwargs):
        data.file_url = S3Storage().get(data.file_name)
        return data
