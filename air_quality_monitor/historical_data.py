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

