import boto3
from uuid import uuid4
from config import BucketSettings
from fastapi import HTTPException, status, UploadFile

bucket_settings = BucketSettings()

SUPPORTED_FILE_TYPES = {
    "image/png": "png",
    "image/jpeg": "jpeg",
    "image/avif": "avif",
    "image/webp": "webp",
}

SESSION = boto3.Session(
    bucket_settings.aws_access_key_id,
    bucket_settings.aws_secret_access_key
)

S3_BUCKET_NAME = bucket_settings.s3_bucket_name
S3 = SESSION.resource('s3')
BUCKET = S3.Bucket(S3_BUCKET_NAME)
MB = 1024 * 1024


def send_image_to_s3(file: UploadFile):
    # checking if file is not empty
    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No file found")

    # checking if file type is supported
    if file.content_type not in SUPPORTED_FILE_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Unsupported file type: {file.content_type}. Supported file types are {SUPPORTED_FILE_TYPES}")

    # uploading file with try_catch
    try:
        # creating unique filename
        filename = f"{uuid4()}.{file.filename.split('.')[-1]}"
        BUCKET.upload_fileobj(file.file, filename, ExtraArgs={
            "ContentType": "image/png",
            "ContentDisposition": "inline"
        })
    except boto3.botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "PutObject:The specified key does already exist":
            print("The object key already exists in the S3 bucket.")
        elif e.response["Error"]["Code"] == "AccessDenied":
            print("AccessDenied to upload the object")
        else:
            raise
    except boto3.botocore.exceptions.EndpointConnectionError as e:
        print("There was an issue with the connection to the S3 service.")
        raise

    uploaded_file_url = f"https://{S3_BUCKET_NAME}.s3.ap-northeast-1.amazonaws.com/{filename}"
    return uploaded_file_url


def delete_image_from_s3(file_url: str):
    file_name = file_url.split("/")[3]
    try:
        BUCKET.delete_objects(Delete={
            'Objects': [
                {
                    'Key': file_name
                }
            ]
        })
    except boto3.botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            print("The object key does not exist.")
        elif e.response["Error"]["Code"] == "AccessDenied":
            print("AccessDenied to delete the object")
        else:
            raise


def update_image_from_s3(file: UploadFile, file_url: str):
    delete_image_from_s3(file_url)
    updated_file_url = send_image_to_s3(file)
    return updated_file_url
