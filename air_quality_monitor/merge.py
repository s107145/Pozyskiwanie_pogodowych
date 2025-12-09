from datetime import datetime
from utils.data_handler import save_json, save_to_db
from air_quality_monitor import gios


def merge_air_quality_data(openaq_data: dict,
                           gios_data: dict,
                           ) -> dict: #scraped_data: dict
    """
    Łączy dane z OpenAQ, GIOŚ i ewentualne dane scrapowane.
    """

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "location": "Opole – ul. Koszyka / os. Armii Krajowej",
        "openaq": openaq_data or {},
        "gios": gios_data or {},
        "scraped": scraped_data or {}
    }


def run_merge(saved_openaq):
    """Pobiera dane z GIOŚ, łączy z OpenAQ i zapisuje wynik."""

    # Pobranie danych GIOŚ
    gios_data =  gios.gios_get_measurements()

    # Jeśli nie masz scrapingu – zostaw jako None
    scraped_data = None

    # Scal dane
    merged = merge_air_quality_data(
        openaq_data=saved_openaq,
        scraped_data=scraped_data,
        gios_data=gios_data
    )

    # Zapisz efekt
    save_json(merged, "data/merged.json")
    save_to_db(merged)

    print("\n=== Połączono dane i zapisano do DB oraz JSON ===\n")

    return merged
