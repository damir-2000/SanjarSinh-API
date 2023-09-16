from pydantic import BaseSettings


class DBSettings(BaseSettings):
    database_user: str
    database_password: str
    database_host: str
    database_port: str
    database_db: str

    class Config:
        env_file = ".env"


class BucketSettings(BaseSettings):
    aws_access_key_id: str
    aws_secret_access_key: str
    s3_bucket_name: str

    class Config:
        env_file = ".env"


class TokenSettings(BaseSettings):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"
