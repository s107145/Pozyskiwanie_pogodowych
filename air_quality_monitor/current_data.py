import time #moduł do obsługi czasu np. sleep
import logging #moduł do logowania informacji, ostrzeżeń i błędów
from sensors import download_current_all_sensors #funkcja pobierające aktualne dane z sensorów
from config import CURRENT_FILE #ścieżka do pliku gdzie są zapisywane dane aktualne
from utils.anomalies import detect_anomalies #funkcja wykrywająca anomalie
from utils.missing_data import handle_missing_data #funkcja radząca sobie z brakami danych
from utils.data_handler import save_json_merge, save_current_to_db #zapis do nadpisywanego pliku json i bazy danych

#Tworzy logger do zapisywania komunikatów w konsoli i pliku
#Raportuje status działania programu
logger = logging.getLogger("air_quality")

def get_current_data():
    """ Funkcja pobiera aktualne dane z sensorów.
     Jeśli się uda - zwraca informację i dane
     Jeśli nie - loguje error i none"""

    try:
        data = download_current_all_sensors()
        logger.info("Pobrano dane aktualne ze wszystkich sensorów.")
        return data
    except Exception as e:
        logger.error(f"Błąd podczas pobierania danych aktualnych: {e}")
        return None


def run_current_monitoring(frequency_sec: int, duration_sec: int = None):
    """Funkcja loguje start monitorungu
    Argumenty: co ile sekund pobiera dane, ile sekund ma trwać monitoring """

    logger.info(f"Start monitoringu aktualnych danych co {frequency_sec} sekund.")

    if duration_sec:
        logger.info(f"Czas działania monitoringu: {duration_sec} sekund.")

    start_time = time.time() #zapisuje czas rozpoczęcia monitoringu (do kontroli jego długości)

    #Pętla działa dopóki nie osiagnie limitu czasu lub użytkwnik jej nie przerwie
    try:
        while True:
            current_data = get_current_data()

#Spr czy dane są poprawne i zawierają results
            if current_data and current_data.get("results"):
                measurements = current_data["results"] #lista pomiarów

                save_json_merge(current_data, CURRENT_FILE) #nadpisywanie pliku json
                save_current_to_db(current_data)#zapisanie do bazy danych
                detect_anomalies(current_data) #wykrywanie anomalii

                logger.info(f"Liczba odebranych pomiarów: {len(measurements)}")
                handle_missing_data(measurements) #uzupełnienie braków lub reakcja  na nie

#Jeśli podano limit czasu, sprawdza czy już minął, jeśli tak loguje konic i przerywa pętle
            if duration_sec is not None:
                if time.time() - start_time >= duration_sec:
                    #time.time - zwraca czas w s od 1.01.1970
                    logger.info("Czas monitoringu dobiegł końca.")
                    break

            time.sleep(frequency_sec) #czeka fs sekund przed kolejnym pobraniem

#Obsługa przerwania przez użytkownika (CTRL+C), loguje warning i kończy program bez błędu
    except KeyboardInterrupt:
        logger.warning("Monitoring danych aktualnych przerwany przez użytkownika.")
