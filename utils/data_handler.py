import shutil
from datetime import datetime
import sqlite3
import json
import os

def save_json(data: dict, path: str):
    """Zapisuje dane do JSON z backupem i obsługą błędów."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    backup_path = path + ".backup"

    # Tworzymy backup starego pliku
    if os.path.exists(path):
        try:
            shutil.copyfile(path, backup_path)
            print(f"Stworzono backup: {backup_path}")
        except Exception as e:
            print(f"Nie udało się utworzyć backupu: {e}")

    # Zapis danych
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Dane zapisane w {path} ({datetime.now()})")
    except Exception as e:
        print(f"Błąd zapisu danych: {e}")
        # Próba odzyskania backupu
        if os.path.exists(backup_path):
            try:
                shutil.copyfile(backup_path, path)
                print(f"Odzyskano plik z backupu po błędzie zapisu.")
            except Exception as e2:
                print(f"Nie udało się odzyskać backupu: {e2}")

def load_json(path: str):
    """Wczytuje dane z JSON. Jeśli plik jest uszkodzony, próbuje backup."""
    if not os.path.exists(path):
        print(f"Plik {path} nie istnieje.")
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Plik {path} jest uszkodzony!")
        backup_path = path + ".backup"
        if os.path.exists(backup_path):
            try:
                with open(backup_path, "r", encoding="utf-8") as f:
                    print(f"Odzyskano dane z backupu: {backup_path}")
                    return json.load(f)
            except Exception as e:
                print(f"Backup również nie działa: {e}")
        return None
    except Exception as e:
        print(f"Błąd wczytywania pliku: {e}")
        return None

#SQL lite


DB_PATH = "data/air_quality.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS air_quality (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            location TEXT,
            openaq TEXT,
            scraped TEXT,
            gios TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_to_db(data: dict):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO air_quality (timestamp, location, openaq, scraped, gios)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data["timestamp"],
        data["location"],
        json.dumps(data["sources"]["openaq"]),
        json.dumps(data["sources"]["scraped"]),
        json.dumps(data["sources"]["gios"])
    ))

    conn.commit()
    conn.close()
