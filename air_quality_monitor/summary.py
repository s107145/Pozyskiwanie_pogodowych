def show_historical_summary(data: dict):
    """Podsumowanie danych historycznych + przykładowe wartości parametrów."""
    results = data.get("results", [])

    print("\n Podsumowanie danych historycznych ")
    print(f"Liczba pomiarów: {len(results)}")
    if not results:
        print("Brak pomiarów w danych historycznych.")

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


