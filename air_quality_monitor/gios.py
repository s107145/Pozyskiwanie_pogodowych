import requests

GIOS_STATION_ID = 754   # Opole – ul. Koszyka

def gios_get_sensors(station_id=GIOS_STATION_ID):
    url = f"https://api.gios.gov.pl/pjp-api/rest/station/sensors/{station_id}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()

def gios_get_measurements(sensor_id):
    url = f"https://api.gios.gov.pl/pjp-api/rest/data/getData/{sensor_id}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()

def get_gios_station_data(station_id=GIOS_STATION_ID):
    sensors = gios_get_sensors(station_id)
    result = {}

    for sensor in sensors:
        param = sensor["param"]["paramCode"]
        sid = sensor["id"]
        try:
            data = gios_get_measurements(sid)
            result[param] = data
        except Exception:
            result[param] = None

    return result
