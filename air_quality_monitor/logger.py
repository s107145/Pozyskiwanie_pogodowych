import logging
from logging.handlers import RotatingFileHandler
import os




# Folder na logi
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "system.log")

# Główny logger aplikacji
logger = logging.getLogger("air_quality")
logger.setLevel(logging.INFO)

# 🔑 KLUCZOWE: zabezpieczenie przed dodawaniem handlerów wiele razy
if not logger.handlers:

    # Handler plikowy z rotacją
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8"
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler konsolowy
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# Opcjonalnie: wyłącz propagację do root loggera
logger.propagate = False
