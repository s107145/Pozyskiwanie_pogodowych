import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler

def clean_invalid(df):
    """Usuwa inf, zamienia je na NaN, usuwa duplikaty."""
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.drop_duplicates()
    return df


def add_features(df):
    """
    Tworzy dodatkowe cechy:
    - zmiana wartości (diff)
    - średnia krocząca
    - kategoria jakości powietrza
    """
    if "value" in df.columns:
        df["value_diff"] = df["value"].diff()
        df["rolling_mean_3"] = df["value"].rolling(window=3).mean()
        df["rolling_mean_6"] = df["value"].rolling(window=6).mean()

    return df


def normalize(df):
    """Normalizacja 0–1."""
    if "value" in df.columns:
        scaler = MinMaxScaler()
        df["value_norm"] = scaler.fit_transform(df[["value"]])
    return df


def standardize(df):
    """Standaryzacja (mean=0, std=1)."""
    if "value" in df.columns:
        scaler = StandardScaler()
        df["value_std"] = scaler.fit_transform(df[["value"]])
    return df

def prepare_features(df):
    """
    1. Czyści dane (usuwa Inf, duplikaty, uzupełnia NaN średnią parametru)
    2. Tworzy dodatkowe cechy (diff, rolling mean)
    3. Normalizuje i standaryzuje wartości (value_norm, value_std)
    4. Zwraca DataFrame gotowy do analizy
    """
    import numpy as np
    import pandas as pd
    from sklearn.preprocessing import MinMaxScaler, StandardScaler

    # Zamień Inf -> NaN i usuń duplikaty
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.drop_duplicates()

    # Grupowanie po parametrze, aby cechy liczyć osobno dla każdego parametru
    result_list = []

    for param_name, group in df.groupby("parameter.name"):
        group = group.copy()

        # Uzupełnij brakujące wartości średnią dla parametru
        if "value" in group.columns:
            mean_val = group["value"].mean()
            group["value"] = group["value"].fillna(mean_val)

            # Feature engineering
            group["value_diff"] = group["value"].diff()
            group["rolling_mean_3"] = group["value"].rolling(window=3).mean()
            group["rolling_mean_6"] = group["value"].rolling(window=6).mean()

            # Normalizacja
            scaler_norm = MinMaxScaler()
            group["value_norm"] = scaler_norm.fit_transform(group[["value"]])

            # Standaryzacja
            scaler_std = StandardScaler()
            group["value_std"] = scaler_std.fit_transform(group[["value"]])

        result_list.append(group)

    df_prepared = pd.concat(result_list, ignore_index=True)
    return df_prepared
