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


settings = Settings()
