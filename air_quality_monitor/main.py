from datetime import datetime, timedelta, timezone

from historical_data import get_historical_data, load_historical_data
from current_data import run_current_monitoring
from utils.data_handler import save_current_to_db

# Domyślny zakres ostatnich 7 dni (gdy użytkownik nic nie wpisze)
default_to = datetime.now(timezone.utc).date()
default_from = (datetime.now(timezone.utc) - timedelta(days=7)).date()

def ask_yes_no(prompt: str) -> bool:
    """
    Pyta użytkownika o odpowiedź tak/nie aż do skutku.
    Zwraca True dla tak, False dla nie.
    """
    while True:
        ans = input(prompt).strip().lower()
        if ans in ("t", "tak", "y", "yes"):
            return True
        elif ans in ("n", "nie", "no"):
            return False
        else:
            print("Nieprawidłowa odpowiedź. Wpisz: tak/nie.")


def ask_date_range():
    print("\n=== Dane historyczne ===")
    date_from = input(f"Data początkowa (YYYY-MM-DD): ").strip()
    date_to = input(f"Data końcowa   (YYYY-MM-DD): ").strip()

    if not date_from:
        date_from = str(default_from)
    if not date_to:
        date_to = str(default_to)

    return date_from, date_to


def show_historical_summary(data: dict):
    """Podsumowanie danych historycznych + przykładowe wartości parametrów."""
    results = data.get("results", [])

    print("\n=== Podsumowanie danych historycznych ===")
    print(f"Liczba pomiarów: {len(results)}")
    if not results:
        print("Brak pomiarów w danych historycznych.")
        print("=========================================\n")
        return

    # Liczba rekordów na parametr
    counts = {}
    for m in results:
        param = m.get("parameter")
        if isinstance(param, dict):
            param = param.get("name") or param.get("id")
        param = param or "BRAK"
        counts[param] = counts.get(param, 0) + 1

    print("Pomiary wg parametrów:")
    for p, c in counts.items():
        print(f"{p}: {c} rekordów")

    # Przykładowe wartości – po 3 ostatnie dla każdego parametru
    print("\nPrzykładowe wartości (3 ostatnie dla każdego parametru):")
    for param_name in counts.keys():
        sample = [
            m for m in results
            if (m.get("parameter").get("name") if isinstance(m.get("parameter"), dict) else m.get("parameter")) == param_name
        ][-3:]  # ostatnie 3

        if not sample:
            continue

        print(f"\n  {param_name}:")
        for m in sample:
            dt_obj = m.get("datetime") or m.get("date")
            if isinstance(dt_obj, dict):
                ts = dt_obj.get("utc") or dt_obj.get("local")
            else:
                ts = dt_obj

            value = m.get("value")
            unit = m.get("unit")
            if not unit and isinstance(m.get("parameter"), dict):
                unit = m["parameter"].get("units")

            # TEN print musi być WEWNĄTRZ pętli for m in sample:
            print(f"{value} {unit}")

    print("=========================================\n")


def main():
    print("======================================")
    print("  Air Quality Monitor – OpenAQ")
    print("======================================")

    # 1. Dane historyczne: wczytaj lub pobierz nowe
    saved = load_historical_data()
    use_saved = False

    if saved:
        print("\nZnaleziono zapisane dane historyczne.")
        use_saved = ask_yes_no("Użyć zapisanych danych historycznych? (tak/nie): ")

        if not use_saved:
            # użytkownik nie chce starych danych → pobierz nowe
            date_from, date_to = ask_date_range()
            saved = get_historical_data(date_from, date_to)
    else:
        # w ogóle nie ma pliku z danymi historycznymi
        print("\nBrak zapisanych danych historycznych – pobieram nowe.")
        date_from, date_to = ask_date_range()
        saved = get_historical_data(date_from, date_to)

    # 🟢 Zapis danych historycznych do SQLite
    from utils.data_handler import save_historical_to_db
    save_historical_to_db(saved)  # <- tutaj zapis do bazy
    print("✔ Dane historyczne zapisane do bazy SQLite")


    # jeżeli tu dotarliśmy, 'saved' powinno zawierać dane (stare lub nowe)
    if not saved:
        print("✗ Nie udało się pobrać danych historycznych. Kończę program.")
        return  # w funkcji main(); poza funkcją użyj sys.exit(1)

    # 1a. Podsumowanie danych historycznych
    show_historical_summary(saved)

    # === FEATURE ENGINEERING (opcjonalnie) ===
    import pandas as pd
    from utils.features import prepare_features

    df = pd.json_normalize(saved["results"])
    df = prepare_features(df)

    columns_to_show = ["parameter.name", "value", "parameter.units", "value_norm", "value_std"]

    print("\n=== Przykładowe nowe cechy (wybrane kolumny) ===")
    for param_name, group in df.groupby("parameter.name"):
        print(f"\n--- {param_name.upper()} ---")
        print(group[columns_to_show].head(5))

    # 2. Monitorowanie danych aktualnych
    print("\n=== Dane aktualne ===")
    freq = input("Podaj częstotliwość pobierania (sekundy) [domyślnie 60 sekund]: ").strip()
    if not freq:
        freq = "60"
    try:
        freq_int = int(freq)
    except ValueError:
        freq_int = 60

    duration = input("Podaj czas trwania monitoringu (minuty, puste = nieskończoność): ").strip()
    if duration:
        try:
            duration_sec = int(duration) * 60  # zamiana minut na sekundy
        except ValueError:
            duration_sec = None
    else:
        duration_sec = None

    current_data = run_current_monitoring(freq_int, duration_sec)
    if current_data:
        save_current_to_db(current_data)  # <- zapis do SQLite
        print("✔ Dane aktualne zapisane do bazy SQLite")

    #Zapis danych do bazy danych
if __name__ == "__main__":
    main()
