import logging #logowanie informacji, ostrzeżeń i błędów
import requests #moduł do wysylania żądań HHTP do API
from sensors import download_historical_all_sensors #funkcja pobierająca dane hist z sensorów (tu mamy url)
from utils.data_handler import load_json #funkcja wczytująca dane z pliku json
from config import HISTORICAL_FILE #ścieżka do pliku z danymi hist


def get_historical_data(date_from: str, date_to: str):
    """Funkcja pobiera dane historyczne między date_from a date_to korzystając z funkcji dhas
    Zwraca wynik w formie danych (słownik)"""
    return download_historical_all_sensors(date_from, date_to)


def load_historical_data():
    """Funkcja wczytuje dane historyczne z pliku JSON.
    Jeśli dane istnieją - komunikat o ich znalezieniu
    Jesli plik jest pusty/ nie istnieje - informuje, że ich nie ma
    Zwraca wczytane dane lub ich brak"""
    data = load_json(HISTORICAL_FILE)
    if data:
        print(f"Znaleziono zapisane dane historyczne w {HISTORICAL_FILE}")
    else:
        print("Brak zapisanych danych historycznych.")
    return data

#Tworzy logger do zapisywania komunikatów w konsoli i pliku
#Raportuje status działania programu
logger = logging.getLogger("air_quality")


def check_api(url: str, timeout: int = 10) -> bool:
    """
    Funkcja sprawdza dostępność API - wysyła żądanie HHTP pod adres url(adres znajduje sie w sensors.py),
    jeśli odp nie będzie w 10s żądanie zost przerwane
    Jeśli wszystko działa - loguje sukres i wraca TRUE
    Jeśli wystąpi problem (timeout, brak połączenia, błąd HTTP lub inny błąd)  loguje problem i zwraca False
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