from tech_challenge_dois.data_transformation import process_and_export_file
from tech_challenge_dois.scraping import download_file


def main() -> None:
    path_downloaded_file = download_file()
    process_and_export_file(filepath=path_downloaded_file)
    return None


if __name__ == "__main__":
    main()
