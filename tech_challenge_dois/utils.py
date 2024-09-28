import functools
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import List, Tuple

from loguru import logger

from tech_challenge_dois.settings import logger_config, settings

# Configure loguru with loaded configuration
logger.configure(**logger_config.model_dump())


# Decorator for logging function entry, exit, and execution time
def log_function(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(f"🏁 INÍCIO: {func.__name__}")

        result = func(*args, **kwargs)

        end_time = time.time()
        run_time = end_time - start_time
        logger.info(f"🏁 FIM: {func.__name__} (🕖 {run_time:.4f}s)")

        return result

    return wrapper


def current_downloaded_csv_files() -> List[Path]:
    download_dir = Path(settings.DOWNLOAD_DIR)
    current_csv_files = list(download_dir.glob("*.csv"))
    return current_csv_files


def already_done_today() -> Tuple[bool, str]:
    utc_now = datetime.now(UTC).strftime(format="%d-%m-%y")

    files = current_downloaded_csv_files()
    f_filter = lambda file: utc_now in str(file)
    files_today = list(filter(f_filter, files))

    if files_today:
        return (True, str(files_today[0].absolute()))

    return False, ""
