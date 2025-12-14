import os #operacje na plikach i katalogach (tworzenie folderów, sprawdzanie ścieżek)
import json # zapis i odczyt danych w formacie JSON.
import shutil # moduł do tworzenia backup-u
import sqlite3 #obsługa bazy danycch SQLite
from datetime import datetime, timezone #klasa dayetime(operacja na czasie) timezone (strefy czasowe)
import logging #logowanie komunikatów
from air_quality_monitor.config import DB_PATH



#Tworzy logger do zapisywania komunikatów w konsoli i pliku
#Raportuje status działania programu
logger = logging.getLogger("air_quality")


# JSON – zapis / odczyt, tworzenie kopii zapasowej
def save_json(data: dict, path: str):
    """Zapisuje dane do JSON z backupem i obsługą błędów.
    Jeśli plik jest uszkodzony lub nie istnieje, próbuje wczytać backup (path + ".backup").
    Jeśli wczytanie backupu też się nie uda, zwraca None."""
    if not os.path.exists(path): #sprawdza czy plik istnieje, jeśli nie nie zwraca nic
        return None
    backup_path = path + ".backup" #tworzy ścieżke do pliku backup

    if os.path.exists(path): #sprawdza czy plik docelowy już istnieje (backup powstaje gsy już jest plik zapisany)
        try:
            shutil.copyfile(path, backup_path) #kopiuje plik i tworzy jego dokładną kopie (nadpisuje juz powstały)
            print(f"Stworzono backup: {backup_path}")
        except Exception as e: #jeśli kopiowanie nie uda się
            print(f"Nie udało się utworzyć backupu: {e}")

    try: #blok try do zapisu danych
        with open(path, "w", encoding="utf-8") as f: #plik do zapisu ("w"), jeśli plik istnieje to nadpisuje
            json.dump(data, f, ensure_ascii=False, indent=4) #zapis danych do JSON, ensure_ascii pl znaki nie są zmieniane, indent (formatowanie)
        print(f"Dane zapisane w {path} ({datetime.now()})")
    except Exception as e:
        print(f"Błąd zapisu danych: {e}")

        if os.path.exists(backup_path):#Sprawdza czy istnieje backup
            try:
                shutil.copyfile(backup_path, path)#kopiuje backup na originalną scieżkę, przywraca ostatnią poprawną wersję
                print("Odzyskano plik z backupu.")
            except Exception as e2:
                print(f"Nie udało się odzyskać backupu: {e2}")




def load_json(path: str):
    """Wczytuje JSON, w razie błędu próbuje backup."""

    if not os.path.exists(path): #sprawdza czy plik istnieje, jeśli nie nie zwraca nic
        return None

    try:#próba odczytu pliku
        with open(path, "r", encoding="utf-8") as f: #"r" tryb odczytu
            return json.load(f) #czyta plik, zamienia JSON na obiekt pythona (dict)

    except json.JSONDecodeError: #błąd gdy plik jest uszkodzony, tworzy ścieżkę do backupu
        backup_path = path + ".backup"

        if os.path.exists(backup_path): #sprawdza czy backup jest dostępny
            try:
                with open(backup_path, "r", encoding="utf-8") as f: #otwiera backup
                    logger.warning("Odzyskano dane z backupu: %s", backup_path)
                    return json.load(f) #wczytanie json z backup, zwraca dane

#wyjątek gdy plik główny i backup jest uszkodzony
            except (OSError, json.JSONDecodeError) as e: #oserror- problem z plikiem,
                logger.error("Nie udało się wczytać backupu %s: %s", backup_path, e)

        return None


def save_json_merge(new_payload: dict, path: str, key: str = "results"):
    """Funkcja nadpisuje dane do istniejących plików.
    new_payload - nowe dane do zapisania
    key="results" - nazwa klucza z listą danych (domyślnie "results", można ją użyć też do innych kluczy)
    """
    existing = load_json(path) #wczytanie obecnego pliku

#czy plik istnieje, czy w danych istniejących jest klucz i czy nowe dane też posiadają klucz(results) - musi być to spelnione do doklejania
    if existing and key in existing and key in new_payload:
        merged = existing[key] + new_payload[key] #łączenie starych i nowych rekordów
    else:#gdy plik nie isnieje/ nie ma klucza/ nowe dane go nie mają
        merged = new_payload.get(key, []) #bierzemy nowe dane, .get(key, []) zabezpiecza przed KeyError

    payload = new_payload.copy() #kopia nowego payload
    payload[key] = merged #zawiera stare i nowe rekordy
    payload["total_measurements"] = len(merged) #informuje o licznie wszystkich rekordów

    save_json(payload, path)#zapis danych



# SQLite



def init_db():
    """Funkcja tworzy bazę danych """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)#tworzy katalog
    conn = sqlite3.connect(DB_PATH) #połączenie z bazą danych
    cur = conn.cursor()#wykonywanie poleceń SQL

#Tworzenie tabeli
    cur.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            location_id INTEGER,
            parameter TEXT,
            value REAL,
            unit TEXT,
            timestamp TEXT
            
        )
    """)

    conn.commit() #zapis zmian w bazie danych (jeśli tego nie będzie to tabela nie zapisałaby się)
    conn.close() #zamyka połączenie z bazą



# Zapis danych historycznych do bazy danych
def save_historical_to_db(payload: dict):
    """Zapisuje dane historyczne do SQLite"""
    init_db() #wywoluje funkcje do tworzenia pliku bazy
    conn = sqlite3.connect(DB_PATH) #otwiera połączenie z bazą
    cur = conn.cursor()#tworzy kursor

    location_id = payload.get("location_id")

    for m in payload.get("results", []): #iteracja po pomiarach, jeśli nie ma result pętla się nie wykona

        # parametr
        param = m.get("parameter")
        if isinstance(param, dict):#pobiera gdy parameter jest słownikiem
            param_name = param.get("name") #pobiera nazwę
            unit = param.get("units") #pobiera jednostkę
        else: #gdy parameter nie jest słownikiem
            param_name = param #waetości bezpośrednie
            unit = m.get("unit") #pobiera z pomiaru

        # timestamp
        dt = m.get("datetime") or m.get("date") #pobranie czasu pomiaru
        if isinstance(dt, dict): #gdy czas jest słownikiem
            timestamp = dt.get("utc") or dt.get("local") #jeśli nie ma czasu UTC bierze lokalny
        else: #gdy nie jest slownikiem
            timestamp = dt

        # Jeśli nadal brak timestamp, używa czasu pobrania
        if not timestamp:
            timestamp = datetime.now(timezone.utc).isoformat()

        # INSERT –  6 kolumn
        #cur.execute - wysyła polecenie SQL
        #wstawia jeden rekord,
        #dodaje nowe wiersze do bazy danych
        #insert - dopisuje na dole
        #???? - miejce na dane (później zostaną dodane przez program)
        cur.execute("""
            INSERT INTO measurements
            (source, location_id, parameter, value, unit, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "historical",
            location_id,
            param_name,
            m.get("value"),
            unit,
            timestamp
        ))

    conn.commit() #zapis zmian
    conn.close() #zamyka połączenie z bazą


# Zapis danych aktualnych do bazy danych

def save_current_to_db(payload: dict):
    """Zapisuje dane aktualne do SQLite."""
    init_db() # wywoluje funkcje do tworzenia pliku bazy
    conn = sqlite3.connect(DB_PATH)# otwiera połączenie z bazą
    cur = conn.cursor()# tworzy kursor

    location_id = payload.get("location_id")
    download_time = payload.get("download_time")#czas pobrania danych

#Iteracja po pomiarach, jeśli result nie istnieje to petla nie wykona się
    for m in payload.get("results", []):

        # parametr
        param = m.get("parameter") #pobiera info o parametrze
        if isinstance(param, dict): #gdy jest słownik
            param_name = param.get("name") #pobiera nazwę
            unit = param.get("units") #jednostkw
        else: #gdy parametr nie jest slownikiem pobiera wartości bezposrednio z pomiaru
            param_name = param
            unit = m.get("unit")

        # ustalenie czasu pomiaru (na początku none)
        timestamp = None
        if isinstance(m.get("datetime"), dict): #jeśli zapis jest w slowniku
            timestamp = m["datetime"].get("utc") or m["datetime"].get("local")

        if not timestamp: #jeśli dalej nie ma czasu
            period = m.get("period") #bierze zakres czasu
            if isinstance(period, list) and period: #czy jest listą/ czt nie jest pusta
                p = period[0] #1 element listy
                timestamp = (  #jeśli wciąż nie ma zakresu bierze koniec lub początek zakresu
                    p.get("datetimeTo", {}).get("utc") #koniec zakresu
                    or p.get("datetimeFrom", {}).get("utc") #początek
                )

        if not timestamp: #jeśli dalej nie ma bierze czas pobrania lub aktualny czas UTC
            timestamp = download_time or   datetime.now(timezone.utc).isoformat()

        # INSERT –  6 kolumn
        # cur.execute - wysyła polecenie SQL
        # wstawia jeden rekord,
        # dodaje nowe wiersze do bazy danych
        # insert - dopisuje na dole
        # ???? - miejce na dane (później zostaną dodane przez program)
        cur.execute("""
            INSERT INTO measurements
            (source, location_id, parameter, value, unit, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "current",
            location_id,
            param_name,
            m.get("value"),
            unit,
            timestamp))
    conn.commit() #zapis zmian
    conn.close() #zamyka połączenie z bazą
