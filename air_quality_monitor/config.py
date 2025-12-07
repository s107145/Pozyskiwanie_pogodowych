import os

OPENAQ_API_KEY = "a9292fce261dce7e515f3ccf8e1903314349b749539962090449c13c4a9e9d5b"
LOCATION_ID = 10580

# Folder na dane
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, "data")

# Utwórz folder data, jeśli nie istnieje
os.makedirs(DATA_FOLDER, exist_ok=True)

HISTORICAL_FILE = os.path.join(DATA_FOLDER, "historical_data.json")
CURRENT_FILE = os.path.join(DATA_FOLDER, "current_data.json")
