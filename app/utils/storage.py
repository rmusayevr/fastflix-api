import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile, HTTPException
from app.core.config import settings


def get_s3_client():
    """
    Creates a Boto3 client.
    If S3_ENDPOINT_URL is set (e.g., MinIO), it uses that.
    Otherwise, it defaults to standard AWS S3.
    """
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )


async def upload_file_to_s3(file: UploadFile, filename: str) -> str:
    """
    Uploads a file to the S3 Bucket and returns the public URL.
    """
    s3_client = get_s3_client()

    try:
        s3_client.upload_fileobj(
            file.file,
            settings.S3_BUCKET_NAME,
            filename,
            ExtraArgs={"ContentType": file.content_type},
        )
    except ClientError as e:
        print(f"Error uploading to S3: {e}")
        raise HTTPException(status_code=500, detail="File upload failed")

    if settings.S3_ENDPOINT_URL:
        base_url = settings.S3_ENDPOINT_URL.replace("minio", "localhost")
        return f"{base_url}/{settings.S3_BUCKET_NAME}/{filename}"
    else:
        # Standard AWS URL format
        return f"https://{settings.S3_BUCKET_NAME}.s3.amazonaws.com/{filename}"
