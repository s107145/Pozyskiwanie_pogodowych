import json
import os

def save_json(data, path: str):
    """Zapisuje dane (dict) do pliku JSON."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_json(path: str):
    """Wczytuje dane z pliku JSON, jeśli istnieje."""
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None
