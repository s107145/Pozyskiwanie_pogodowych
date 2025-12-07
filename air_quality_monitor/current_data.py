import time
from datetime import datetime
import json
import os

from config import CURRENT_FILE
from sensors import download_current_all_sensors
from utils.anomalies import detect_anomalies
from utils.missing_data import handle_missing_data


def save_current_data(new_data: dict):
    """Zapisuje aktualne dane do pliku JSON z deduplikacją."""
    if not new_data:
        return

    # Zapisz bezpośrednio (bez skomplikowanej deduplikacji na razie)
    os.makedirs(os.path.dirname(CURRENT_FILE), exist_ok=True)
    with open(CURRENT_FILE, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=4)

    print(f"{datetime.now()} - Zapisano aktualne dane do {CURRENT_FILE}")


def get_current_data():
    return download_current_all_sensors()


# def run_current_monitoring(frequency_sec: int):
#     """
#     Pętla pobierania danych aktualnych z wszystkimi sensorami.
#     """
#     print(f"\nStart monitoringu danych aktualnych co {frequency_sec} s. (Ctrl+C aby przerwać)\n")
#     try:
#         while True:
#             current_data = get_current_data()
#             if current_data:
#                 save_current_data(current_data)
#                 detect_anomalies(current_data)
#
#                 measurements = current_data.get("results", [])
#
#                 # Poprawione wypisywanie z datami i jednostkami
#                 print("\n=== Aktualne pomiary (wszystkie sensory) ===")
#                 for m in measurements:
#                     param = m.get("parameter")
#                     if isinstance(param, dict):
#                         param = param.get("name") or param.get("id")
#
#                     # Poprawiona data
#                     dt_obj = m.get("datetime") or m.get("date")
#                     if isinstance(dt_obj, dict):
#                         dt = dt_obj.get("utc") or dt_obj.get("local")
#                     else:
#                         dt = dt_obj
#
#                     # Poprawiona jednostka
#                     unit = m.get("unit")
#                     if not unit and isinstance(m.get("parameter"), dict):
#                         unit = m["parameter"].get("units")
#
#                     value = m.get("value")
#                     print(f"{param} = {value} {unit}")
#                 print("===========================================\n")
#
#                 handle_missing_data(measurements)
#
#             time.sleep(frequency_sec)
#
#     except KeyboardInterrupt:
#         print("\nMonitoring danych aktualnych przerwany przez użytkownika.")
#
#

import time


def run_current_monitoring(frequency_sec: int, duration_sec: int = None):
    """
    Pętla pobierania danych aktualnych z wszystkimi sensorami.
    Jeśli duration_sec jest None, działa w nieskończoność.
    """
    print(f"\nStart monitoringu danych aktualnych co {frequency_sec} s.\n")

    start_time = time.time()

    try:
        while True:
            current_data = get_current_data()
            if current_data:
                save_current_data(current_data)
                detect_anomalies(current_data)

                measurements = current_data.get("results", [])

                print("\n=== Aktualne pomiary (wszystkie sensory) ===")
                for m in measurements:
                    param = m.get("parameter")
                    if isinstance(param, dict):
                        param = param.get("name") or param.get("id")

                    dt_obj = m.get("datetime") or m.get("date")
                    if isinstance(dt_obj, dict):
                        dt = dt_obj.get("utc") or dt_obj.get("local")
                    else:
                        dt = dt_obj

                    unit = m.get("unit")
                    if not unit and isinstance(m.get("parameter"), dict):
                        unit = m["parameter"].get("units")

                    value = m.get("value")
                    print(f"{param} = {value} {unit}")
                print("===========================================\n")

                handle_missing_data(measurements)

            # Sprawdzenie, czy minął czas trwania
            if duration_sec is not None:
                elapsed = time.time() - start_time
                if elapsed >= duration_sec:
                    print("\nCzas monitoringu dobiegł końca.")
                    break

            time.sleep(frequency_sec)

    except KeyboardInterrupt:
        print("\nMonitoring danych aktualnych przerwany przez użytkownika.")
