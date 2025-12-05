from datetime import datetime, timedelta, timezone

from historical_data import get_historical_data, load_historical_data
from current_data import run_current_monitoring


# Domyślny zakres ostatnich 7 dni (gdy użytkownik nic nie wpisze)
default_to = datetime.now(timezone.utc).date()
default_from = (datetime.now(timezone.utc) - timedelta(days=7)).date()


def ask_date_range():
    print("\n=== Dane historyczne ===")
    date_from = input(f"Data początkowa (YYYY-MM-DD) [{default_from}]: ").strip()
    date_to = input(f"Data końcowa   (YYYY-MM-DD) [{default_to}]: ").strip()

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
        print(f"\nZnaleziono zapisane dane historyczne.")
        answer = input("Użyć zapisanych danych historycznych? (tak/nie): ").strip().lower()
        if answer in ["", "tak", "t", "yes", "y"]:
            use_saved = True

    if not use_saved:
        date_from, date_to = ask_date_range()
        saved = get_historical_data(date_from, date_to)

    # POKAŻ PODSUMOWANIE DANYCH HISTORYCZNYCH
    if saved:
        show_historical_summary(saved)
    else:
        print("\nBrak danych historycznych do wyświetlenia.\n")

    # 2. Monitorowanie danych aktualnych
    print("\n=== Dane aktualne ===")
    freq = input("Podaj częstotliwość pobierania (sekundy) [60]: ").strip()
    if not freq:
        freq = "60"
    try:
        freq_int = int(freq)
    except ValueError:
        freq_int = 60

    run_current_monitoring(freq_int)


if __name__ == "__main__":
    main()
