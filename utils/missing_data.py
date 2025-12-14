import pandas as pd
def handle_missing_data(measurements: list):
    """
    Obsługa brakujących danych w aktualnej porcji pomiarów.
    - Konwertuje listę słowników do DataFrame.
    - Uzupełnia braki w kolumnie 'value' średnią.
    Zwraca DataFrame.
    Funkcja przyjmuje listę słowników
    """
    if not measurements: #jeśli lista jest pusta/None wyświetla komunikat i konczy działanie
        print("Brak danych do obsługi brakujących wartości.")
        return None

    df = pd.json_normalize(measurements) #zamiana listy słowników na tabelę
    # słownik w liście staje się wierszem, a klucze słowników stają się kolumnami.

    if "value" in df.columns:
        if df["value"].isna().any(): #spr czy w kolumnie value sa braki
            mean_value = df["value"].mean() #oblicza średną
            df["value"] = df["value"].fillna(mean_value) #wypełnienie Nan wart średniej
            print(f"Uzupełniono brakujące wartości 'value' średnią = {mean_value:.2f}")
    else:
        print("Brak kolumny 'value' w danych – nic nie uzupełniono.")

    return df
