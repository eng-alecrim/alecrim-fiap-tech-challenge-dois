import re
import unicodedata
from pathlib import Path

import pandas as pd
from loguru import logger

from tech_challenge_dois.aws_utils import save_on_s3
from tech_challenge_dois.settings import logger_config, settings
from tech_challenge_dois.utils import log_function

logger.configure(**logger_config.model_dump())


def read_csv_file(csv_path: str) -> pd.DataFrame:
    return pd.read_csv(
        csv_path,
        encoding="latin1",
        sep=";",
        skiprows=1,
        skipfooter=2,
        engine="python",
    )


def rename_column_name(input_str: str) -> str:
    input_str = str(input_str)
    # Normalizando o texto conforme a forma NFKD
    nfkd_form = unicodedata.normalize("NFKD", input_str)
    output_str = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    # Removendo as possíveis tags de HTML
    regex_tags = r"</?.>"
    output_str = re.sub(regex_tags, "", output_str)
    # Substituindo os caracteres especiais e números (tudo o que NÃO estiver de A-z)
    regex = re.compile(r"[^a-zA-Z0-9\s]+")
    tokens = regex.sub(" ", output_str).split()

    # Removendo possíveis espaços em branco no início e/ou fim da str
    output_str = " ".join(map(lambda x: x.strip(), tokens))

    # Retorna algo apenas se o resultado NÃO for uma str vazia
    return output_str.replace(" ", "_").upper()


@log_function
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

    column_rename_mapping = dict(
        zip(df_final.columns, map(rename_column_name, df_final.columns))
    )
    df_final.rename(columns=column_rename_mapping, inplace=True)

    return df_final


@log_function
def process_and_export_file(filepath: str) -> None:
    logger.debug(
        f"process_and_export_file: Carregando e tratando o arquivo '{filepath}' . . ."
    )
    df_raw = read_csv_file(filepath)
    df_final = data_transformation(df_raw)
    logger.success("process_and_export_file: Arquivo carregado e tratado.")

    filename = Path(filepath).stem
    destination_path = f"{settings.PARQUET_FILES_DIR}/{filename}.parquet"
    logger.debug(
        f"process_and_export_file: Salvando o arquivo em '{destination_path}' . . ."
    )
    df_final.to_parquet(destination_path, engine="fastparquet")
    logger.success("process_and_export_file: Arquivo salvo.")

    if settings.SAVE_ON_AWS_S3_BUCKET:
        logger.debug(
            "process_and_export_file: Salvando o arquivo em no S3 da AWS . . ."
        )
        save_on_s3(filename=filename, origin_file_path=destination_path)
        logger.success("process_and_export_file: Arquivo salvo.")
        if settings.REMOVE_LOCAL_AFTER_SAVE_ON_S3:
            logger.debug("process_and_export_file: Removendo os arquivos locais . . .")
            Path(filepath).unlink()
            Path(destination_path).unlink()
            logger.success("process_and_export_file: Arquivos removidos.")

    return None
