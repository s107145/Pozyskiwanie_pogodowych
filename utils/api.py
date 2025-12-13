import time
import requests
from air_quality_monitor.logger import logger


def safe_request(
    url: str,
    headers: dict = None,
    params: dict = None,
    max_retries: int = 5,
    backoff_factor: int = 2,
    timeout: int = 30
):
    """
    Bezpieczne wywołanie API:
    - obsługuje limity (429)
    - retry z backoff
    - timeout
    - logowanie błędów
    """
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=timeout
            )

            # LIMIT API
            if response.status_code == 429:
                wait_time = backoff_factor ** attempt
                logger.warning(
                    f"Limit API (429). Próba {attempt}/{max_retries}. "
                    f"Czekam {wait_time}s."
                )
                time.sleep(wait_time)
                continue

            # Błędy serwera
            if response.status_code >= 500:
                logger.warning(
                    f"Błąd serwera {response.status_code}. "
                    f"Próba {attempt}/{max_retries}."
                )
                time.sleep(backoff_factor)
                continue

            return response

        except requests.exceptions.Timeout:
            logger.warning(
                f"Timeout API. Próba {attempt}/{max_retries}."
            )
            time.sleep(backoff_factor)

        except requests.exceptions.RequestException as e:
            logger.error(f"Błąd połączenia API: {e}")
            return None

    logger.error("Przekroczono maksymalną liczbę prób API.")
    return None
