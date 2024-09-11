from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    DOWNLOAD_DIR: str
    PARQUET_FILES_DIR: str
    MAX_RETRIES: int
    SELENIUM_FIREFOX_URL: str
    URL_B3: str
    HEADLESS_WEBDRIVER: bool
    RUN_ON_HOUR: int
    RUN_ON_MINUTE: int
    SAVE_ON_AWS_S3_BUCKET: bool = False
    REMOVE_LOCAL_AFTER_SAVE_ON_S3: Optional[bool] = False
    AWS_ACCESS_KEY: Optional[str] = None
    AWS_SECRET_KEY: Optional[str] = None
    AWS_SESSION_TOKEN: Optional[str] = None
    BUCKET_NAME: Optional[str] = None
    BUCKET_FILE_DIRECTORY: Optional[str] = None


settings = Settings()
