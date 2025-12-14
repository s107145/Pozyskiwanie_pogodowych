import logging
import requests
from sensors import download_historical_all_sensors
from utils.data_handler import load_json
from config import HISTORICAL_FILE


def get_historical_data(date_from: str, date_to: str):
    return download_historical_all_sensors(date_from, date_to)


def load_historical_data():
    data = load_json(HISTORICAL_FILE)
    if data:
        print(f"Znaleziono zapisane dane historyczne w {HISTORICAL_FILE}")
    else:
        print("Brak zapisanych danych historycznych.")
    return data


logger = logging.getLogger("air_quality")


def check_api(url: str, timeout: int = 10) -> bool:
    """
    Sprawdza dostępność API.
    Zwraca True jeśli API działa, False w przeciwnym wypadku.
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()

        logger.info("Połączono z API OpenAQ.")
        return True

    except requests.exceptions.Timeout:
        logger.error("Przekroczono czas oczekiwania na API OpenAQ.")
    except requests.exceptions.ConnectionError:
        logger.error("Brak połączenia z API OpenAQ.")
    except requests.exceptions.HTTPError as e:
        logger.error(f"Błąd HTTP API OpenAQ: {e}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Nieoczekiwany błąd API OpenAQ: {e}")

    return False