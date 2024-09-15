import boto3
from botocore.exceptions import ClientError
from loguru import logger

from tech_challenge_dois.settings import logger_config, settings

logger.configure(**logger_config.model_dump())


def s3_file_exists(file_key: str) -> bool:
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
        aws_session_token=settings.AWS_SESSION_TOKEN,
    )

    try:
        s3_client.head_object(Bucket=settings.BUCKET_NAME, Key=file_key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        else:
            logger.critical(f"s3_file_exists: ARQUIVO NÃO FOI SALVO! Erro -> {e}")
            raise Exception(e)


def save_on_s3(filename: str, origin_file_path: str) -> None:
    s3_file_path = (
        f"{settings.BUCKET_FILE_DIRECTORY}/{filename}.parquet"
        if settings.BUCKET_FILE_DIRECTORY
        else f"{filename}.parquet"
    )

    if s3_file_exists(file_key=s3_file_path):
        logger.debug("save_on_s3: Arquivo já existe na AWS.")
        return None

    s3 = boto3.resource(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
        aws_session_token=settings.AWS_SESSION_TOKEN,
    )

    bucket = s3.Bucket(settings.BUCKET_NAME)

    logger.debug("save_on_s3: Salvando o arquivo na AWS . . .")
    with open(origin_file_path, "rb") as data:
        bucket.put_object(Key=s3_file_path, Body=data)
    logger.success("save_on_s3: Arquivo salvo na AWS.")

    return None
