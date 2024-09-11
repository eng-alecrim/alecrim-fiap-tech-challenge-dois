from pathlib import Path

import pandas as pd

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


def process_and_export_file(filepath: str) -> None:
    df_raw = read_csv_file(filepath)
    df_final = data_transformation(df_raw)

    filename = Path(filepath).stem
    destination_path = f"{settings.PARQUET_FILES_DIR}/{filename}.parquet"
    df_final.to_parquet(destination_path, engine="fastparquet")

    return None
