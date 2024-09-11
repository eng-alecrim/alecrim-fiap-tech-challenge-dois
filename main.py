import time

from tech_challenge_dois.data_transformation import process_and_export_file
from tech_challenge_dois.scheduler import already_ran_today, time_to_run
from tech_challenge_dois.scraping import download_file

SLEEP_HOURS = 23
SLEEP_MINUTES = 50
SLEEP_TIME_AFTER_RUN = 60 * 60 * SLEEP_HOURS + 60 * SLEEP_MINUTES  # 23h50min
SLEEP_TIME_WAITING = 60


def main() -> None:
    while True:
        if time_to_run():
            if not already_ran_today():
                path_downloaded_file = download_file()
                process_and_export_file(filepath=path_downloaded_file)
            time.sleep(SLEEP_TIME_AFTER_RUN)
        time.sleep(SLEEP_TIME_WAITING)


if __name__ == "__main__":
    main()
