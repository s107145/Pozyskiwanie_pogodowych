import logging #moduł do logowania informacji, błędów i ostrzeżeń
from logging.handlers import RotatingFileHandler # handler do logów zapisanych w pliku z automatyczną rotacją
                                                # (przy osiągnięciu limitu rozmiaru tworzy kopie starszych logów)
import os #moduł do pracy z systemem plików (tworzenie katalogów, łączenie ścieżek).

def setup_logger( name: str = "air_quality", log_dir: str = "logs",
                  log_file: str = "system.log", level: int = logging.INFO) -> logging.Logger:
    """
    Funcja konfiguruje i zwraca logger aplikacji (logging.Logger).
    log_dir - tworzy katalog, w ktorym są zapisywane pliki logów
    log_file- nazwa pliku logi
    level - poziom logowania"""

    # Utworzenie katalogu na logi
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)

    logger = logging.getLogger(name) #pobiera looger (jeśli nie istnieje, tworzy nowy)
    logger.setLevel(level) #ustawia poiom logowania (np. info)

    #  zabezpieczenie przed wielokrotnym dodaniem handlerów
    #Sprawdza czy logger ma jakies handlery (ma - zwraca istniejący logger, żeby nie dublować czy kolejnych wywolaniach)
    if logger.handlers:
        return logger

#Określenie formatu logów
#"%(asctime)s - czas (do milisekundy)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # Handler plikowy z rotacją
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=5 * 1024 * 1024,  #zapisuje logi do pliku i robi rotację, gdy plik osiągnie 5 MB.
        backupCount=3, #zachowuje 3 starsze wersje plików logów.
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter) #ustawia wcześniej zdefiniowany format logów

    # Handler konsoli
    #Logi wyświetlaja się w konsoli, format taki sam jak w pliku
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    #Dodaje handler plikowy i konsoli do loggera (logi trafiają w 2 miejsca jednocześnie)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Zapobieganie wysyłania logów do globalnego logera Pythona(root logger)
    #Logi nie dubluja się w konsoli)
    logger.propagate = False
    return logger


