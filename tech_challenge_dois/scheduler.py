from datetime import datetime, timedelta

import pytz

from tech_challenge_dois.settings import settings

BRAZIL_TIME_ZONE = pytz.timezone("America/Sao_Paulo")


def time_to_run() -> bool:
    today = datetime.today().date()

    scheduled_time = BRAZIL_TIME_ZONE.localize(
        datetime.combine(today, datetime.min.time())
        + timedelta(
            hours=settings.RUN_ON_HOUR, minutes=settings.RUN_ON_MINUTE, seconds=00
        )
    )

    current_time = datetime.now(BRAZIL_TIME_ZONE)

    delta = scheduled_time - current_time

    return delta <= timedelta(0)
