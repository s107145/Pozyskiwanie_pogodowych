from user import ask_yes_no,ask_date_range
from historical_data import get_historical_data, load_historical_data
from current_data import run_current_monitoring
from utils.data_handler import save_current_to_db
from summary import show_historical_summary
from utils.data_handler import save_historical_to_db
import pandas as pd
from utils.features import prepare_features


def main():

    print("  Air Quality Monitor – OpenAQ")


    # 1. Dane historyczne: wczytaj lub pobierz nowe
    saved = load_historical_data()


    if saved:
        print("\nZnaleziono zapisane dane historyczne.")
        use_saved = ask_yes_no()

        if not use_saved:
            # użytkownik nie chce starych danych → pobierz nowe
            date_from, date_to = ask_date_range()
            saved = get_historical_data(date_from, date_to)
    else:
        # w ogóle nie ma pliku z danymi historycznymi
        print("\nBrak zapisanych danych historycznych – pobieram nowe.")
        date_from, date_to = ask_date_range()
        saved = get_historical_data(date_from, date_to)

    #  Zapis danych historycznych do SQLite

    save_historical_to_db(saved)  # <- tutaj zapis do bazy
    print(" Dane historyczne zapisane do bazy SQLite")


    # jeżeli tu dotarliśmy, 'saved' powinno zawierać dane (stare lub nowe)
    if not saved:
        print(" Nie udało się pobrać danych historycznych. Kończę program.")
        return  # w funkcji main(); poza funkcją użyj sys.exit(1)

    # 1a. Podsumowanie danych historycznych
    show_historical_summary(saved)

    # === FEATURE ENGINEERING (opcjonalnie) ===

    df = pd.json_normalize(saved["results"])
    df = prepare_features(df)

    columns_to_show = ["parameter.name", "value", "parameter.units", "value_norm", "value_std"]

    print("\n Przykładowe nowe cechy (wybrane kolumny) ")
    for param_name, group in df.groupby("parameter.name"):
        print(f"\n {param_name.upper()} ")
        print(group[columns_to_show].head(5))

    # 2. Monitorowanie danych aktualnych
    print("\n Dane aktualne ")
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
        print(" Dane aktualne zapisane do bazy SQLite")

    #Zapis danych do bazy danych
if __name__ == "__main__":
    main()
