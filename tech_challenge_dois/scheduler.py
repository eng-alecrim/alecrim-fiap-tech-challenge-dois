from datetime import datetime, timedelta
from pathlib import Path

import pytz

from tech_challenge_dois.settings import settings

BRAZIL_TIME_ZONE = pytz.timezone("America/Sao_Paulo")
TODAY = datetime.today().date()


def time_to_run() -> bool:
    scheduled_time = BRAZIL_TIME_ZONE.localize(
        datetime.combine(TODAY, datetime.min.time())
        + timedelta(
            hours=settings.RUN_ON_HOUR, minutes=settings.RUN_ON_MINUTE, seconds=00
        )
    )

    current_time = datetime.now(BRAZIL_TIME_ZONE)

    delta = scheduled_time - current_time

    return delta <= timedelta(0)


def already_ran_today() -> bool:
    dir_data = Path(settings.PARQUET_FILES_DIR)
    for file in dir_data.glob(f"*{TODAY.strftime("%d-%m-%y")}*.parquet"):
        if file:
            return True
    return False
