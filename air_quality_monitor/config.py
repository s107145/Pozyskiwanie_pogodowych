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
DB_PATH = "data/air_quality.db"

# Progi orientacyjne (WHO 2021 / UE – w µg/m³) [upraszczamy do jednego progu "wysokiego"]
THRESHOLDS = {
    "no2": 200,   # 1h limit UE, WHO nadal uznaje 200 1h [web:3][web:6]
    "o3": 100,    # WHO: 8h średnia 100 µg/m³ [web:4][web:6][web:12]
    "so2": 125,   # UE: 24h 125, WHO 24h 40 – możesz zaostrzyć, jeśli chcesz [web:3][web:6]
    "co": 4000,   # WHO: 24h 4 mg/m³ = 4000 µg/m³ [web:6][web:16]
    "bc": 20,     # brak oficjalnego WHO – przykładowy niski próg „ostrożnościowy”
}

