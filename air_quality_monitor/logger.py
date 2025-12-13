import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logger(
    name: str = "air_quality",
    log_dir: str = "logs",
    log_file: str = "system.log",
    level: int = logging.INFO
) -> logging.Logger:
    """
    Konfiguruje i zwraca logger aplikacji.
    """

    # Utworzenie katalogu na logi
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 🔑 zabezpieczenie przed wielokrotnym dodaniem handlerów
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # Handler plikowy z rotacją
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # Handler konsolowy
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Brak propagacji do root loggera
    logger.propagate = False

    return logger


