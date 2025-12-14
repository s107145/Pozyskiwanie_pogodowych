from datetime import datetime, timezone, timedelta
def ask_yes_no():
    """
    Pyta użytkownika o odpowiedź tak/nie aż do skutku.
    Zwraca True dla tak, False dla nie.
    """
    while True:
        ans = input("Użyć zapisanych danych historycznych? (tak/nie): ").strip().lower()
        if ans in ("t", "tak", "y", "yes"):
            return True
        elif ans in ("n", "nie", "no"):
            return False
        else:
            print("Nieprawidłowa odpowiedź. Wpisz: tak/nie.")

# Domyślny zakres ostatnich 7 dni (gdy użytkownik nic nie wpisze)
default_to = datetime.now(timezone.utc).date() #domyśln data końcowa (aktualna)
default_from = (datetime.now(timezone.utc) - timedelta(days=7)).date()
#(datetime.now- pobiera aktualną datę i godzine
#timezone.utc - uniwersalny czas UTC (nie lokalnej strefie komputera)
#- timedelta(days=7)).date() odejmuje 7 dni od aktualnego czasu
def ask_date_range():
    """Funkcja prosi użytkownika o wpisane daty początkowej i koncowej"""
    print("\n Dane historyczne ")
    date_from = input(f"Data początkowa (YYYY-MM-DD): ").strip()
    date_to = input(f"Data końcowa   (YYYY-MM-DD): ").strip()

#Sprawdzenie czy date_from i date_to jest pusta/ None, jeśli jest pusta to używa domyślnego zakreesu dat
    if not date_from:
        date_from = str(default_from)
    if not date_to:
        date_to = str(default_to)

    return date_from, date_to
