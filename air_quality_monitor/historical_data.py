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


# from logger import logger
#
# try:
#     r = requests.get(url)
#     logger.info("Połączono z API OpenAQ.")
# except Exception as e:
#     logger.error(f"Błąd API: {e}")
