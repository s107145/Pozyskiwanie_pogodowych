import os
import json
import shutil
import sqlite3
from datetime import datetime


# =========================
# JSON – zapis / odczyt
# =========================

def save_json(data: dict, path: str):
    """Zapisuje dane do JSON z backupem i obsługą błędów."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    backup_path = path + ".backup"

    if os.path.exists(path):
        try:
            shutil.copyfile(path, backup_path)
            print(f"Stworzono backup: {backup_path}")
        except Exception as e:
            print(f"Nie udało się utworzyć backupu: {e}")

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Dane zapisane w {path} ({datetime.now()})")
    except Exception as e:
        print(f"Błąd zapisu danych: {e}")
        if os.path.exists(backup_path):
            try:
                shutil.copyfile(backup_path, path)
                print("Odzyskano plik z backupu.")
            except Exception as e2:
                print(f"Nie udało się odzyskać backupu: {e2}")


def load_json(path: str):
    """Wczytuje JSON, w razie błędu próbuje backup."""
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        backup_path = path + ".backup"
        if os.path.exists(backup_path):
            try:
                with open(backup_path, "r", encoding="utf-8") as f:
                    print("Odzyskano dane z backupu.")
                    return json.load(f)
            except Exception:
                pass
        return None


def save_json_merge(new_payload: dict, path: str, key: str = "results"):
    """Dokleja nowe rekordy do istniejącego pliku JSON."""
    existing = load_json(path)

    if existing and key in existing and key in new_payload:
        merged = existing[key] + new_payload[key]
    else:
        merged = new_payload.get(key, [])

    payload = new_payload.copy()
    payload[key] = merged
    payload["total_measurements"] = len(merged)

    save_json(payload, path)


# =========================
# SQLite – konfiguracja
# =========================

DB_PATH = "data/air_quality.db"


def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            location_id INTEGER,
            parameter TEXT,
            value REAL,
            unit TEXT,
            timestamp TEXT,
            raw_json TEXT
        )
    """)

    conn.commit()
    conn.close()


# =========================
# Zapis danych historycznych
# =========================

def save_historical_to_db(payload: dict):
    """Zapisuje dane historyczne do SQLite."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    location_id = payload.get("location_id")

    for m in payload.get("results", []):

        param = m.get("parameter")
        if isinstance(param, dict):
            param_name = param.get("name")
            unit = param.get("units")
        else:
            param_name = param
            unit = m.get("unit")

        dt = m.get("datetime") or m.get("date")
        if isinstance(dt, dict):
            timestamp = dt.get("utc") or dt.get("local")
        else:
            timestamp = dt

        cur.execute("""
            INSERT INTO measurements
            (source, location_id, parameter, value, unit, timestamp, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "historical",
            location_id,
            param_name,
            m.get("value"),
            unit,
            timestamp,
            json.dumps(m)
        ))

    conn.commit()
    conn.close()


# =========================
# Zapis danych aktualnych (POPRAWNE)
# =========================

def save_current_to_db(payload: dict):
    """
    Zapisuje dane aktualne do SQLite – poprawna obsługa OpenAQ v3.
    Gwarantuje brak NULL w timestamp.
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    location_id = payload.get("location_id")
    download_time = payload.get("download_time")

    for m in payload.get("results", []):

        # parametr
        param = m.get("parameter")
        if isinstance(param, dict):
            param_name = param.get("name")
            unit = param.get("units")
        else:
            param_name = param
            unit = m.get("unit")

        # timestamp
        timestamp = None

        if isinstance(m.get("datetime"), dict):
            timestamp = m["datetime"].get("utc") or m["datetime"].get("local")

        if not timestamp:
            period = m.get("period")
            if isinstance(period, list) and period:
                p = period[0]
                timestamp = (
                    p.get("datetimeTo", {}).get("utc")
                    or p.get("datetimeFrom", {}).get("utc")
                )

        if not timestamp:
            timestamp = download_time or datetime.utcnow().isoformat()

        cur.execute("""
            INSERT INTO measurements
            (source, location_id, parameter, value, unit, timestamp, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "current",
            location_id,
            param_name,
            m.get("value"),
            unit,
            timestamp,
            json.dumps(m)
        ))

    conn.commit()
    conn.close()
