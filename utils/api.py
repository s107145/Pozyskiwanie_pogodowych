import requests #moduł do wysylania żądań HHTP do API
import time #moduł do obsługi czasu np. sleep
import logging #moduł do logowania informacji, ostrzeżeń i błędów


#Tworzy logger do zapisywania komunikatów w konsoli i pliku
#Raportuje status działania programu
logger = logging.getLogger("air_quality")

def safe_request(url: str,headers: dict | None = None, params: dict | None = None, max_retries: int = 5,
    backoff_factor: int = 2, timeout: int = 30) -> requests.Response | None:
    """
    Bezpieczne wywołanie API:
    - retry + exponential backoff
    - obsługa limitów
    - timeout
    - czytelne logowanie
    """

    for attempt in range(1, max_retries + 1): #Pętla sprawdza probę połączenia max 5 razy
        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=timeout
            )

            # LIMIT API
            if response.status_code == 429: #too many requests
                wait_time = backoff_factor ** attempt #czeka attmpt^2
                logger.warning(
                    "Limit API (429). Próba %s/%s. Czekam %ss.",
                    attempt, max_retries, wait_time
                )
                time.sleep(wait_time)
                continue

            # Błędy serwera (retry)
            # 500 - internal server error
            #502 - Bad Gateway
            #503 – Service Unavailable
            if 500 <= response.status_code < 600:
                wait_time = backoff_factor ** attempt
                logger.warning(
                    "Błąd serwera %s. Próba %s/%s. Czekam %ss.",
                    response.status_code, attempt, max_retries, wait_time
                )
                time.sleep(wait_time)
                continue

            # Inne błędy klienta – NIE retry np. 400, 401, 404
            if 400 <= response.status_code < 500:
                logger.error(
                    "Błąd klienta %s: %s",
                    response.status_code, response.text
                )
                return None

            return response

        except requests.exceptions.Timeout: #serwer nie odpowiedział na czas
            wait_time = backoff_factor ** attempt
            logger.warning(
                "Timeout API. Próba %s/%s. Czekam %ss.",
                attempt, max_retries, wait_time
            )
            time.sleep(wait_time)

        except requests.exceptions.RequestException as e: #inne błędy sieciowe, np. brak internetu ,zerwane połączenie
            logger.error("Błąd połączenia API: %s", e)
            return None

    logger.error("Przekroczono maksymalną liczbę prób API.")
    return None
