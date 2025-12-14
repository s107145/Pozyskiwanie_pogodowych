from datetime import datetime #klasa datetime z modulu datetime umożliwia pracę z datami/czasem
from air_quality_monitor.config import THRESHOLDS

def detect_anomalies(data):
    """
    Funcja przyjmuje słownik data z wynikami.
    Wykrywa anomalie na podstawie progów dla konkretnych parametrów (THRESHOLDS).
    """
    anomalies = [] #pusta lista
    results = data.get("results", []) #lista pomiarów pobranych z klucza results danych

#Iteracja po wszystkich pomiarach
    for item in results:
        value = item.get("value")
        # wyciągamy obiekt parametru
        param_obj = item.get("parameter") or item.get("parameterId") #może być dist lub wart id

        if isinstance(param_obj, dict): #jeśli param_obj jest słownikiem (spr nazwę lub id)
            param_name = (param_obj.get("name") or param_obj.get("id") or "").lower()
            unit = param_obj.get("units") or item.get("unit") #jednostka
        else: #jeśli nie dict, jest traktowany jako nazwa paramteru i pobiera jednostkę z item
            param_name = str(param_obj).lower() if param_obj else ""
            unit = item.get("unit")

        # Pobranie daty pomiaru
        dt_obj = item.get("datetime") or item.get("date") #sprawdza datetime lub date
        if isinstance(dt_obj, dict): #slownik - pobiera czas lokalny
            ts = dt_obj.get("utc") or dt_obj.get("local")
        else:
            ts = dt_obj

        # brak wartości
        if value is None: #jeśli brak wartości, dodaje go do listy anomalies z opisem Brak wartosci)
            anomalies.append((ts, param_name, value, "Brak wartości", unit))
            continue

        # Sprawdzenie przekroczenia progu
        threshold = THRESHOLDS.get(param_name)
        if threshold is not None and value > threshold: #jeśli istnieje i przekroczenie parametru
            anomalies.append(
                (ts, param_name, value, f"Przekroczenie progu {threshold} {unit}", unit)
            ) #dodanie anomalię do listy anomalii

#Jeśli lista anomalii nie jest pusta wyświetla komunikat, polazuje czas, nazwe, wartośc,powód i jednostke
    if anomalies:
        print("\nALERT: Wykryto anomalie w danych aktualnych ")
        for ts, param_name, value, reason, unit in anomalies:
            print(f"  {ts} | {param_name.upper()} = {value:.2f} {unit}  ({reason})")

    else: #jeśli nie ma anomalii wyświetla komunikat
        print(f"{datetime.utcnow()} - Brak anomalii w danych aktualnych.")

    return anomalies