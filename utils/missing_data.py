import pandas as pd
def handle_missing_data(measurements: list):
    """
    Obsługa brakujących danych w aktualnej porcji pomiarów.
    - Konwertuje listę słowników do DataFrame.
    - Uzupełnia braki w kolumnie 'value' średnią.
    Zwraca DataFrame.
    """
    if not measurements:
        print("Brak danych do obsługi brakujących wartości.")
        return None

    df = pd.json_normalize(measurements)

    if "value" in df.columns:
        if df["value"].isna().any():
            mean_value = df["value"].mean()
            df["value"] = df["value"].fillna(mean_value)
            print(f"Uzupełniono brakujące wartości 'value' średnią = {mean_value:.2f}")
    else:
        print("Brak kolumny 'value' w danych – nic nie uzupełniono.")

    return df
