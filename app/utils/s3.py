import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.cache import cache

from app.utils.constants import CacheKeys

session = boto3.session.Session(
    region_name=settings.AWS_S3_REGION_NAME,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)
s3_client = session.client("s3")


def generate_presigned_url(
    object_name, bucket_name=settings.AWS_STORAGE_BUCKET_NAME, expiration=3600
):
    """
    Generate a presigned URL S3 object upload.

    :param object_name: string
    :param bucket_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """
    # Cache the presigned URL to avoid calling S3 API again.
    cache_key = CacheKeys.SIGNED_URL_CACHE.format(object_name=object_name)
    signed_url = cache.get(cache_key)
    if not signed_url:
        try:
            signed_url = s3_client.generate_presigned_post(
                Bucket=bucket_name,
                Key=object_name,
                Conditions=[
                    ["content-length-range", 0, 100000000],  # around 100MB
                ],
                ExpiresIn=expiration,
            )
            # Cache for 1 min less than actual expiration time to avoid sending stale URL
            cache.set(cache_key, signed_url, timeout=expiration - 60)
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None
    return signed_url
