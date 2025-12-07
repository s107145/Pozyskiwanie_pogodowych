import logging
from logging.handlers import RotatingFileHandler
import os

# Tworzymy folder na logi
os.makedirs("logs", exist_ok=True)

# Główny logger aplikacji
logger = logging.getLogger("air_quality")
logger.setLevel(logging.INFO)

# Handler zapisujący logi do pliku z rotacją
handler = RotatingFileHandler(
    "logs/system.log",      # plik z logami
    maxBytes=5 * 1024 * 1024,   # 5 MB – po przekroczeniu tworzy backup
    backupCount=3,             # ile kopii trzymać
    encoding="utf-8"
)

# Format logów
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)

handler.setFormatter(formatter)
logger.addHandler(handler)

# Logi również na konsoli (opcjonalne)
console = logging.StreamHandler()
console.setFormatter(formatter)
logger.addHandler(console)
