from abc import ABC, abstractmethod
from datetime import timedelta
import boto3
from .config import get_settings


class ObjectStorage(ABC):
    @abstractmethod
    def put(self, key: str, body: bytes, content_type: str) -> str: ...

    @abstractmethod
    def signed_download_url(self, key: str, expires: timedelta = timedelta(minutes=15)) -> str: ...


class S3ObjectStorage(ObjectStorage):
    def __init__(self):
        settings = get_settings()
        self.bucket = settings.s3_bucket
        self.client = boto3.client(
            "s3", endpoint_url=settings.s3_endpoint,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
        )

    def put(self, key: str, body: bytes, content_type: str) -> str:
        self.client.put_object(Bucket=self.bucket, Key=key, Body=body, ContentType=content_type)
        return key

    def signed_download_url(self, key: str, expires: timedelta = timedelta(minutes=15)) -> str:
        return self.client.generate_presigned_url(
            "get_object", Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=int(expires.total_seconds())
        )
