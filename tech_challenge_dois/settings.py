from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings, JsonConfigSettingsSource, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    DOWNLOAD_DIR: str
    PARQUET_FILES_DIR: str
    MAX_RETRIES: int
    SELENIUM_FIREFOX_URL: str
    HEADLESS_WEBDRIVER: bool
    URL_B3: str
    SAVE_ON_AWS_S3_BUCKET: bool = False
    REMOVE_LOCAL_AFTER_SAVE_ON_S3: Optional[bool] = False
    AWS_ACCESS_KEY: Optional[str] = None
    AWS_SECRET_KEY: Optional[str] = None
    AWS_SESSION_TOKEN: Optional[str] = None
    BUCKET_NAME: Optional[str] = None
    BUCKET_FILE_DIRECTORY: Optional[str] = None


settings = Settings()


class LoggerHandlersBase(BaseModel):
    sink: str
    level: str
    format: str
    colorize: bool | None = None
    backtrace: bool | None = None


class LoggerHandlersToDisk(LoggerHandlersBase):
    rotation: str
    retention: str


class LoggerConfig(BaseModel):
    handlers: List[LoggerHandlersBase | LoggerHandlersToDisk]


logger_config = LoggerConfig(
    **JsonConfigSettingsSource(
        settings_cls=BaseSettings,
        json_file="configs/log_config.json",
        json_file_encoding="utf-8",
    ).init_kwargs
)

Path(logger_config.handlers[0].sink).parent.mkdir(exist_ok=True, parents=True)
