import json
import random
import time

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


# --- Lista proxy ---
PROXIES = [
    "93.190.206.3:8080",
    "51.158.68.68:8811",
    "163.172.182.164:8811",
    None,  # możliwość połączenia bez proxy
]

# --- Ścieżka do ChromeDriver ---
CHROMEDRIVER_PATH = r"C:\Users\Natalia\Downloads\chrome-win64\chrome-win64"

# --- Lista URL-i do scrapowania ---
URLS = [
    "https://air-quality.com/place/poland/opole/bb703a04?lang=en&standard=aqi_us",
    "https://air-quality.com/place/poland/opole/bb703a04?lang=en&standard=aqi_us",
    "https://air-quality.com/place/poland/opole/bb703a04?lang=en&standard=aqi_us",
]

RESULTS: list[dict] = []


def analyze_robots(url: str) -> bool:
    domain = url.split("/")[2]
    robots_url = f"https://{domain}/robots.txt"

    print(f"\nPobieram robots.txt z: {robots_url}")

    try:
        r = requests.get(robots_url, timeout=5)
        robots = r.text

        disallowed: list[str] = []
        for line in robots.split("\n"):
            line = line.strip()
            if line.lower().startswith("disallow"):
                parts = line.split(":", 1)
                if len(parts) == 2:
                    rule = parts[1].strip()
                    disallowed.append(rule)

        print("\nZablokowane ścieżki:")
        for d in disallowed:
            print("  ", d or "/")

        for d in disallowed:
            if d and d != "/" and d in url:
                print("\nUWAGA! Scrapowanie tego URL jest zablokowane przez robots.txt\n")
                return False

        print("\n✔ Scrapowanie dozwolone wg robots.txt\n")
        return True

    except Exception as e:
        print("[Scraping] Błąd analizy robots.txt:", e)
        return True


def get_driver(proxy: str | None = None) -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    if proxy:
        options.add_argument(f"--proxy-server=http://{proxy}")

    service = Service(executable_path=CHROMEDRIVER_PATH)
    return webdriver.Chrome(service=service, options=options)


def run_scraping():
    for url in URLS:
        if not analyze_robots(url):
            print(f"[Scraping] POMIJAM {url} – zabronione w robots.txt\n")
            continue

        proxy = random.choice(PROXIES)
        print(f"\n[Scraping] Scrapuję: {url} przez proxy: {proxy}")

        driver = None
        try:
            driver = get_driver(proxy)
            driver.get(url)
            time.sleep(5)

            # Tytuł strony jako dowód działania
            page_title = driver.title

            header_text = None
            try:
                header_elem = driver.find_element(By.TAG_NAME, "h1")
                header_text = header_elem.text.strip()
            except Exception:
                try:
                    header_elem = driver.find_element(By.TAG_NAME, "h2")
                    header_text = header_elem.text.strip()
                except Exception:
                    pass

            RESULTS.append(
                {
                    "url": url,
                    "proxy_used": proxy,
                    "page_title": page_title,
                    "header": header_text,
                }
            )

            print(f"[Scraping] Tytuł strony: {page_title}")
            print(f"[Scraping] Nagłówek: {header_text}")

            time.sleep(random.uniform(2, 4))

        except Exception as e:
            print("[Scraping] Błąd scrapingu:", e)

        finally:
            if driver:
                driver.quit()

    with open("aqi_data.json", "w", encoding="utf-8") as f:
        json.dump(RESULTS, f, ensure_ascii=False, indent=4)

    print("\nZakończono. Dane zapisane w aqi_data.json\n")


if __name__ == "__main__":
    run_scraping()
