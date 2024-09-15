from loguru import logger

from tech_challenge_dois.data_transformation import process_and_export_file
from tech_challenge_dois.scraping import download_file
from tech_challenge_dois.settings import logger_config
from tech_challenge_dois.utils import (
    already_done_today,
    log_function,
)

logger.configure(**logger_config.model_dump())


@log_function
def main() -> None:
    already_done, path_downloaded_file = already_done_today()

    if not already_done:
        path_downloaded_file = download_file()

    process_and_export_file(filepath=path_downloaded_file)

    return None


if __name__ == "__main__":
    main()
