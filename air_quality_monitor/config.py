import os

OPENAQ_API_KEY = "592da2f4df898124a2024c99f033cbde2474f89e15fe1f14b9fa6c254714be22"
LOCATION_ID = 10580

# Folder na dane
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, "data")

# Utwórz folder data, jeśli nie istnieje
os.makedirs(DATA_FOLDER, exist_ok=True)

HISTORICAL_FILE = os.path.join(DATA_FOLDER, "historical_data.json")
CURRENT_FILE = os.path.join(DATA_FOLDER, "current_data.json")
