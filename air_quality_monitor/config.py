""" Plik konfiguracyjny
przechowuje stałe oraz paramtery, które są wykorzystywane w projekcie."""

import os #moduł umożliwia wykonywanie operacji na systemie plików tj. tworzenie katalogów, zarządzanie ścieżkami plików

#Klucz API do serwisu OPENAQ, wykorzyatywany do autoryzacji zapytań o dane dot. jakości powietrza
OPENAQ_API_KEY = "a9292fce261dce7e515f3ccf8e1903314349b749539962090449c13c4a9e9d5b"
#identyfikator lokalizacji Opole, os. Armii Krajowej ul. Koszyka
LOCATION_ID = 10580

# Tworzenie folderu, w ktorym znajduje się plik skryptu
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, "data")

# Utwórz folder data, jeśli nie istnieje
os.makedirs(DATA_FOLDER, exist_ok=True)

#Tworzenie ścieżki do konkretnych plików w folderze data
HISTORICAL_FILE = os.path.join(DATA_FOLDER, "historical_data.json")
CURRENT_FILE = os.path.join(DATA_FOLDER, "current_data.json")
DB_PATH = os.path.join(DATA_FOLDER, "air_quality.db")


# Progi orientacyjne (WHO 2021 / UE – w µg/m³)
THRESHOLDS = {
    "no2": 200,
    "o3": 100,
    "so2": 125,
    "co": 4000,
    "bc": 20,
}

