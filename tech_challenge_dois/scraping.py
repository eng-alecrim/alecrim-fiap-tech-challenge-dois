import time
from pathlib import Path
from typing import Callable, Optional, Tuple

from loguru import logger
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tech_challenge_dois.settings import logger_config, settings
from tech_challenge_dois.utils import (
    current_downloaded_csv_files,
    log_function,
)

Path(settings.DOWNLOAD_DIR).mkdir(exist_ok=True, parents=True)
logger.configure(**logger_config.model_dump())


def webdriver_options(headless: bool) -> Options:
    options = webdriver.FirefoxOptions()
    if headless:
        options.add_argument("-headless")
    options.set_preference(
        "browser.helperApps.neverAsk.saveToDisk",
        "application/pdf, application/octet-stream",
    )

    return options


def get_webdriver(headless: bool = True) -> WebDriver:
    server = settings.SELENIUM_FIREFOX_URL
    options = webdriver_options(headless)
    driver = webdriver.Remote(command_executor=server, options=options)
    return driver


def scroll_into_view_and_click(
    webdriver: WebDriver, identifier: Tuple[str, str], timeout: int = 10
) -> None:
    wait = WebDriverWait(webdriver, timeout)
    button = wait.until(EC.visibility_of_element_located(identifier))
    webdriver.execute_script(
        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button
    )
    button.click()
    return None


@log_function
def wait_for_download(counter: int = 0) -> Optional[Callable]:
    if counter > settings.MAX_RETRIES:
        return None
    for not_finished in Path(settings.DOWNLOAD_DIR).rglob("*.part"):
        if not_finished:
            time.sleep(1.5)
            counter += 1
            return wait_for_download(counter)
    return None


@log_function
def download_file(headless: bool = settings.HEADLESS_WEBDRIVER) -> str:
    current_csv_files = current_downloaded_csv_files()

    webdriver = get_webdriver(headless=headless)
    logger.debug("download_file: Navegador aberto.")
    webdriver.get(settings.URL_B3)

    dropdown_identifier = ("xpath", "//*[@id='segment']")
    scroll_into_view_and_click(webdriver, dropdown_identifier)
    logger.debug("download_file: Botão de dropdown ativado.")

    setor_atuacao_identifier = ("css selector", "#segment > option:nth-child(2)")
    scroll_into_view_and_click(webdriver, setor_atuacao_identifier)
    logger.debug("download_file: 'Setor de Atuação' selecionado.")

    download_button_identifier = ("xpath", "//a[text()='Download']")
    scroll_into_view_and_click(webdriver, download_button_identifier)
    logger.debug("download_file: Download iniciado.")

    logger.debug("download_file: Aguardando o fim do download . . .")
    wait_for_download()
    logger.debug("download_file: Download concluído!.")

    downloaded_file = [
        file
        for file in Path(settings.DOWNLOAD_DIR).glob("*.csv")
        if file not in current_csv_files
    ]

    webdriver.quit()
    logger.debug("download_file: Navegador encerrado.")

    return str(downloaded_file[0].absolute())
