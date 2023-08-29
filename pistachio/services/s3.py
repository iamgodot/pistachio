from logging import getLogger

from boto3.session import Session
from botocore.exceptions import ClientError

from pistachio.settings import settings

LOGGER = getLogger(__name__)


class S3Storage:
    _instance = None
    _client = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            session = Session(
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION_NAME,
            )
            cls._client = session.client("s3")
        return cls._instance

    @property
    def client(self):
        return self._client

    def write(self, key, file_obj):
        self.client.upload_fileobj(file_obj, settings["S3_BUCKET_NAME"], key)

    def get(self, key, expiration=3600) -> str | None:
        try:
            response = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": settings["S3_BUCKET_NAME"], "Key": key},
                ExpiresIn=expiration,
            )
            return response
        except ClientError as e:
            LOGGER.exception(e)
