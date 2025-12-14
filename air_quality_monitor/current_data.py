import time
import logging
from sensors import download_current_all_sensors
from config import CURRENT_FILE
from utils.anomalies import detect_anomalies
from utils.missing_data import handle_missing_data
from utils.data_handler import save_json_merge, save_current_to_db


logger = logging.getLogger("air_quality")

def get_current_data():
    try:
        data = download_current_all_sensors()
        logger.info("Pobrano dane aktualne ze wszystkich sensorów.")
        return data
    except Exception as e:
        logger.error(f"Błąd podczas pobierania danych aktualnych: {e}")
        return None


def run_current_monitoring(frequency_sec: int, duration_sec: int = None):
    logger.info(f"Start monitoringu aktualnych danych co {frequency_sec} sekund.")

    if duration_sec:
        logger.info(f"Czas działania monitoringu: {duration_sec} sekund.")

    start_time = time.time()

    try:
        while True:
            current_data = get_current_data()

            if current_data and current_data.get("results"):
                measurements = current_data["results"]

                save_json_merge(current_data, CURRENT_FILE)
                save_current_to_db(current_data)
                detect_anomalies(current_data)

                logger.info(f"Liczba odebranych pomiarów: {len(measurements)}")
                handle_missing_data(measurements)

            if duration_sec is not None:
                if time.time() - start_time >= duration_sec:
                    logger.info("Czas monitoringu dobiegł końca.")
                    break

            time.sleep(frequency_sec)

    except KeyboardInterrupt:
        logger.warning("Monitoring danych aktualnych przerwany przez użytkownika.")
