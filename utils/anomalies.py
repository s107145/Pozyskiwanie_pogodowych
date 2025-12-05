from datetime import datetime

# Progi orientacyjne (WHO 2021 / UE – w µg/m³) [upraszczamy do jednego progu "wysokiego"]
THRESHOLDS = {
    "no2": 200,   # 1h limit UE, WHO nadal uznaje 200 1h [web:3][web:6]
    "o3": 100,    # WHO: 8h średnia 100 µg/m³ [web:4][web:6][web:12]
    "so2": 125,   # UE: 24h 125, WHO 24h 40 – możesz zaostrzyć, jeśli chcesz [web:3][web:6]
    "co": 4000,   # WHO: 24h 4 mg/m³ = 4000 µg/m³ [web:6][web:16]
    "bc": 20,     # brak oficjalnego WHO – przykładowy niski próg „ostrożnościowy”
}


def detect_anomalies(data):
    """
    Wykrywa anomalie na podstawie progów dla konkretnych parametrów (THRESHOLDS).
    """
    anomalies = []
    results = data.get("results", [])

    for item in results:
        value = item.get("value")
        # wyciągamy obiekt parametru
        param_obj = item.get("parameter") or item.get("parameterId")

        if isinstance(param_obj, dict):
            param_name = (param_obj.get("name") or param_obj.get("id") or "").lower()
            unit = param_obj.get("units") or item.get("unit")
        else:
            param_name = str(param_obj).lower() if param_obj else ""
            unit = item.get("unit")

        # czas pomiaru
        dt_obj = item.get("datetime") or item.get("date")
        if isinstance(dt_obj, dict):
            ts = dt_obj.get("utc") or dt_obj.get("local")
        else:
            ts = dt_obj

        # brak wartości
        if value is None:
            anomalies.append((ts, param_name, value, "Brak wartości", unit))
            continue

        # próg dla danego parametru (jeśli nie ma, pomijamy)
        threshold = THRESHOLDS.get(param_name)
        if threshold is not None and value > threshold:
            anomalies.append(
                (ts, param_name, value, f"Przekroczenie progu {threshold} {unit}", unit)
            )

    if anomalies:
        print("\n=== ALERT: Wykryto anomalie w danych aktualnych ===")
        for ts, param_name, value, reason, unit in anomalies:
            print(f"  {ts} | {param_name.upper()} = {value:.2f} {unit}  ({reason})")
        print("===================================================\n")
    else:
        print(f"{datetime.utcnow()} - Brak anomalii w danych aktualnych.")

    return anomalies