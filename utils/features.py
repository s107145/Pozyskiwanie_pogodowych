import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler
#MinMaxScaler - normalizacja wartości do przedziału [0, 1].
# StandardScaler - standaryzacja (wartości mają średnią 0 i odchylenie standardowe 1).

def prepare_features(df):
    """
    Funkcja przyjmuje df z pomiarami.
    1. Czyści dane (usuwa Inf, duplikaty, uzupełnia NaN średnią parametru)
    2. Tworzy dodatkowe cechy (diff, rolling mean)
    3. Normalizuje i standaryzuje wartości (value_norm, value_std)
    4. Zwraca DataFrame gotowy do analizy
    """

    # Zamień Inf -> NaN i usuń duplikaty
    df = df.replace([np.inf, -np.inf], np.nan) #zamiana wart +/-inf na Nan
    df = df.drop_duplicates() #usuwa duplikaty

    # Grupowanie po parametrze, aby cechy liczyć osobno dla każdego parametru
    result_list = [] #pusta lista do przechowyania przetworzonych grup (powstanie z niej df)

    for param_name, group in df.groupby("parameter.name"): #dzieli dane na grupy wg parametru
        group = group.copy() #Tworzymy kopię każdej grupy, aby nie zmieniać oryginalnego df

        # Uzupełnij brakujące wartości średnią dla parametru
        if "value" in group.columns: #spr czy value istnieje
            mean_val = group["value"].mean() #oblicza srendia dla parametru
            group["value"] = group["value"].fillna(mean_val) #wypełnia Nan średnią

            # Feature engineering - tworzenie dodatkowych cech
            group["value_diff"] = group["value"].diff()#różnica między pomiarami (trendy)
            #Rolling mean pomaga wygładzić dane i wykryć trend zamiast pojedynczych skoków wartości.
            group["rolling_mean_3"] = group["value"].rolling(window=3, center=True, min_periods=1).mean()
            group["rolling_mean_6"] = group["value"].rolling( window=6, center=True, min_periods=1).mean()

            # Normalizacja
            scaler_norm = MinMaxScaler() #przekształca wartości do przedziału [0, 1].
            group["value_norm"] = scaler_norm.fit_transform(group[["value"]])
            #tworzy kolumne value_norm ktora będzie zawierać przekształcone (normalizowane) wartości z kolumny "value".
            #fit_transform - fit() → oblicza min i max wartości w kolumnie "value":,
            #transform() przekształca wart z przedziału [0,1] wg wzoru xnorm = x-min/max-min
            # Standaryzacja
            scaler_std = StandardScaler() #przekształca wart- średnia 0 i odch stand 1.
            group["value_std"] = scaler_std.fit_transform(group[["value"]])

        result_list.append(group) #kazda przetworzona grupa jest dodawana do result_list

    df_prepared = pd.concat(result_list, ignore_index=True) #łączenie grup w 1 df
    return df_prepared
