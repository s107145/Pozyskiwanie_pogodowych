from datetime import datetime
from typing import List, Dict
from config import OPENAQ_API_KEY, LOCATION_ID, HISTORICAL_FILE, CURRENT_FILE
from utils.data_handler import  save_json_merge
from utils.api import safe_request

def get_sensors_for_location(location_id: int) -> List[Dict]:
    """
    Pobiera listę wszystkich sensorów (czujników) dla danej stacji.
    Zwraca listę słowników z polami m.in. id, parameter itp.
    """
    print(f"\nSzukam sensorów dla lokalizacji {location_id}...")

    url = f"https://api.openaq.org/v3/locations/{location_id}/sensors"
    headers = {
        "X-API-Key": OPENAQ_API_KEY,
        "Accept": "application/json",
    }
    params = {
        "limit": 100,
    }

    try:
        response = safe_request(url, headers=headers, params=params)
        if response is None:
            return []
        if response.status_code == 200:
            data = response.json()
            sensors = data.get("results", [])
            print(f"Znaleziono {len(sensors)} sensorów:")
            for sensor in sensors:
                sensor_id = sensor.get("id")
                parameter = sensor.get("parameter", {}).get("name", "nieznany")
                print(f"  - Sensor #{sensor_id}: mierzy {parameter.upper()}")
            return sensors
        else:
            print(f" Błąd: Status code {response.status_code}")
            return []
    except Exception as e:
        print(f" Wystąpił błąd podczas pobierania sensorów: {e}")
        return []


def get_measurements_for_sensor(
    sensor_id: int,
    start_date: str,
    end_date: str,
) -> List[Dict]:
    """
    Pobiera historyczne pomiary z jednego sensora.
    """
    print(f"   Pobieram pomiary z sensora #{sensor_id}...")

    url = f"https://api.openaq.org/v3/sensors/{sensor_id}/measurements"
    headers = {
        "X-API-Key": OPENAQ_API_KEY,
        "Accept": "application/json",
    }
    params = {
        "date_from": f"{start_date}T00:00:00Z",
        "date_to": f"{end_date}T23:59:59Z",
        "limit": 1000,
        "order_by": "datetime",
        "sort": "asc",
    }

    try:
        response = safe_request(url, headers=headers, params=params)
        if response is None:
            return []

        if response.status_code == 200:
            data = response.json()
            measurements = data.get("results", [])
            print(f"     Pobrano {len(measurements)} pomiarów")
            return measurements
        else:
            print(f"     Błąd: Status code {response.status_code}")
            return []
    except Exception as e:
        print(f"     Wystąpił błąd podczas pobierania pomiarów: {e}")
        return []


def download_historical_all_sensors(date_from: str, date_to: str) -> Dict:
    """
    Pobiera dane historyczne ze WSZYSTKICH sensorów i WYŚWIETLA WYNIKI NATYCHMIAST.
    """
    print(f"\n Pobieram dane historyczne {date_from} - {date_to} dla wszystkich sensorów...")

    sensors = get_sensors_for_location(LOCATION_ID)
    all_measurements = []

    print(f"\n Pobieranie danych z {len(sensors)} sensorów:")
    print("-" * 60)

    for s in sensors:
        sensor_id = s.get("id")
        parameter_obj = s.get("parameter", {})
        parameter_name = parameter_obj.get("name", "nieznany").upper()

        if sensor_id is None:
            continue

        print(f"\n Sensor #{sensor_id} ({parameter_name}):")
        measurements = get_measurements_for_sensor(sensor_id, date_from, date_to)

        # NATYCHMIAST WYŚWIETL PODSUMOWANIE
        print_sensor_summary(measurements, sensor_id, parameter_name)

        all_measurements.extend(measurements)

    payload = {
        "location_id": LOCATION_ID,
        "download_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date_from": date_from,
        "date_to": date_to,
        "sensors_count": len(sensors),
        "total_measurements": len(all_measurements),
        "results": all_measurements,
    }

    save_json_merge(payload, HISTORICAL_FILE)
    print(f"\n ZAPISANO {len(all_measurements)} pomiarów do: {HISTORICAL_FILE}")

    return payload


def download_current_all_sensors() -> Dict:
    """
    Pobiera AKTUALNE dane ze wszystkich sensorów lokalizacji
    (po jednym „ostatnim zestawie” z każdego sensora) i zapisuje do CURRENT_FILE.
    """
    sensors = get_sensors_for_location(LOCATION_ID)
    all_measurements = []

    for s in sensors:
        sensor_id = s.get("id")
        if sensor_id is None:
            continue

        # bieżące pomiary dla sensora – bez zakresu dat, tylko limit
        url = f"https://api.openaq.org/v3/sensors/{sensor_id}/measurements"
        headers = {
            "X-API-Key": OPENAQ_API_KEY,
            "Accept": "application/json",
        }
        params = {
            "limit": 100,
            "order_by": "datetime",
            "sort": "desc",
        }

        try:
            response = safe_request(url, headers=headers, params=params)
            if response is None:
                return {}
            print(f"Status current (sensor {sensor_id}): {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                measurements = data.get("results", [])
                all_measurements.extend(measurements)
            else:
                print(f"  Błąd dla sensora {sensor_id}: {response.status_code}")
        except Exception as e:
            print(f"  Błąd przy pobieraniu aktualnych danych sensora {sensor_id}: {e}")

    payload = {
        "location_id": LOCATION_ID,
        "download_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "results": all_measurements,
    }

    save_json_merge(payload, HISTORICAL_FILE)
    print(f"\nZapisano aktualne dane wszystkich sensorów do: {CURRENT_FILE}")
    return payload


def print_sensor_summary(measurements, sensor_id, parameter_name):
    """Wyświetla podsumowanie i próbkę 5 ostatnich pomiarów dla sensora."""
    if not measurements:
        print(f"     Brak pomiarów dla sensora #{sensor_id}")
        return

    print(f"      {parameter_name.upper()}: {len(measurements)} pomiarów")

    # Statystyki
    values = [m.get("value") for m in measurements if m.get("value") is not None]
    if values:
        print(f"       Średnia: {sum(values) / len(values):.2f}")
        print(f"       Min: {min(values):.2f} | Max: {max(values):.2f}")

    # 5 najnowszych pomiarów
    print("       Ostatnie 5 pomiarów:")
    for i, m in enumerate(measurements[-5:], 1):
        period = m.get("period", {})
        dt_obj = None

        # Spróbuj datetimeTo
        if "datetimeTo" in period and isinstance(period["datetimeTo"], dict):
            dt_obj = period["datetimeTo"].get("utc") or period["datetimeTo"].get("local")

        # Jeśli brak To – spróbuj From
        if not dt_obj and "datetimeFrom" in period and isinstance(period["datetimeFrom"], dict):
            dt_obj = period["datetimeFrom"].get("utc") or period["datetimeFrom"].get("local")

        # Gdyby nadal nic — fallback
        if not dt_obj:
            dt_obj = "BRAK_DATY"


        value = m.get("value")
        print(f"         {i}.  {value:.2f}")
