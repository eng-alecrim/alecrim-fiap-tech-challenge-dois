from pathlib import Path

import boto3
import pandas as pd
from botocore.exceptions import ClientError

from tech_challenge_dois.settings import settings


def read_csv_file(csv_path: str) -> pd.DataFrame:
    return pd.read_csv(
        csv_path,
        encoding="latin1",
        sep=";",
        skiprows=1,
        skipfooter=2,
        engine="python",
    )


def data_transformation(df_raw: pd.DataFrame) -> pd.DataFrame:
    original_columns = df_raw.columns.to_list() + ["to_drop"]

    df = df_raw.reset_index()
    columns_to_rename = df.columns.to_list()
    columns_mapping = dict(zip(columns_to_rename, original_columns))
    df_final = df.rename(columns=columns_mapping).drop(columns=["to_drop"])

    df_final["Qtde. Teórica"] = df_final["Qtde. Teórica"].apply(
        lambda x: x.replace(".", "")
    )
    df_final["Part. (%)"] = df_final["Part. (%)"].apply(lambda x: x.replace(",", "."))
    df_final["Part. (%)Acum."] = df_final["Part. (%)Acum."].apply(
        lambda x: x.replace(",", ".")
    )

    columns_dtype_mapping = dict(
        zip(
            original_columns,
            ["category", "category", "category", "category", int, float, float],
        )
    )
    df_final = df_final.astype(columns_dtype_mapping)

    return df_final


def s3_file_exists(file_key: str) -> bool:
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_ACCESS_KEY,
        aws_session_token=settings.AWS_SESSION_TOKEN,
    )

    try:
        s3_client.head_object(Bucket=settings.BUCKET_NAME, Key=file_key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        else:
            return False  # TODO: Loggar este erro em algum lugar


def save_on_s3(filename: str, origin_file_path: str) -> None:
    s3_file_path = (
        f"{settings.BUCKET_FILE_DIRECTORY}/{filename}.parquet"
        if settings.BUCKET_FILE_DIRECTORY
        else f"{filename}.parquet"
    )

    if s3_file_exists(file_key=s3_file_path):
        return None

    s3 = boto3.resource(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
        aws_session_token=settings.AWS_SESSION_TOKEN,
    )
    bucket = s3.Bucket(settings.BUCKET_NAME)

    with open(origin_file_path, "rb") as data:
        bucket.put_object(Key=s3_file_path, Body=data)

    return None


def process_and_export_file(filepath: str) -> None:
    df_raw = read_csv_file(filepath)
    df_final = data_transformation(df_raw)

    filename = Path(filepath).stem
    destination_path = f"{settings.PARQUET_FILES_DIR}/{filename}.parquet"
    df_final.to_parquet(destination_path, engine="fastparquet")

    if settings.SAVE_ON_AWS_S3_BUCKET:
        save_on_s3(filename=filename, origin_file_path=destination_path)
        if settings.REMOVE_LOCAL_AFTER_SAVE_ON_S3:
            Path(filepath).unlink()
            Path(destination_path).unlink()

    return None
