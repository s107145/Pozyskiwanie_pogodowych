
import os #umożliwia operacje na ścieżkach plików i folderach w systemie.

OPENAQ_API_KEY = "a9292fce261dce7e515f3ccf8e1903314349b749539962090449c13c4a9e9d5b"
LOCATION_ID = 10580

# Folder na dane
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, "data")

# Utwórz folder data, jeśli nie istnieje
os.makedirs(DATA_FOLDER, exist_ok=True)

HISTORICAL_FILE = os.path.join(DATA_FOLDER, "historical_data.json")
CURRENT_FILE = os.path.join(DATA_FOLDER, "current_data.json")
DB_PATH = "data/air_quality.db"

# Progi orientacyjne (WHO 2021 / UE – w µg/m³)
THRESHOLDS = {
    "no2": 200,
    "o3": 100,
    "so2": 125,
    "co": 4000,
    "bc": 20,
}

