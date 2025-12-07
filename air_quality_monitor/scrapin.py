import json
import random
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# --- Lista proxy ---
proxies = [
    "93.190.206.3:8080",
    "51.158.68.68:8811",
    "163.172.182.164:8811"
]

# --- Ścieżka do ChromeDriver ---
chromedriver_path = r"C:\Users\natal\Downloads\chromedriver-win64\chromedriver.exe"

# --- Lista URL-i do scrapowania ---
urls = [
    "https://air-quality.com/place/poland/opole/bb703a04?lang=en&standard=aqi_us",
    "https://air-quality.com/place/poland/opole/bb703a04?lang=en&standard=aqi_us",
    "https://air-quality.com/place/poland/opole/bb703a04?lang=en&standard=aqi_us"
]

results = []


# --- Analiza robots.txt ---
def analyze_robots(url):
    domain = url.split("/")[2]
    robots_url = f"https://{domain}/robots.txt"

    print(f"\nPobieram robots.txt z: {robots_url}\n")

    try:
        r = requests.get(robots_url, timeout=5)
        robots = r.text
        print(robots)

        disallowed = []
        for line in robots.split("\n"):
            if line.lower().startswith("disallow"):
                rule = line.split(":")[1].strip()
                disallowed.append(rule)

        print("\nZablokowane ścieżki:")
        for d in disallowed:
            print(" ❌", d)

        # sprawdzamy, czy aktualny URL jest zabroniony
        for d in disallowed:
            if d != "/" and d in url:
                print("\n⚠ UWAGA! Scrapowanie tego URL jest zablokowane przez robots.txt\n")
                return False

        print("\n✔ Scrapowanie dozwolone wg robots.txt\n")
        return True

    except Exception as e:
        print("Błąd analizy robots.txt:", e)
        return True  # jeśli robots.txt nie działa – pozwalamy


# --- Funkcja tworząca driver Chrome z proxy ---
def get_driver(proxy=None):
    options = Options()
    options.add_argument("--headless")  # tryb bez okna
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    if proxy:
        options.add_argument(f'--proxy-server=http://{proxy}')

    service = Service(executable_path=chromedriver_path)
    return webdriver.Chrome(service=service, options=options)


# --- Scrapowanie danych AQI ---
for url in urls:

    # sprawdzamy robots.txt
    if not analyze_robots(url):
        print(f"POMIJAM {url} – zabronione w robots.txt\n")
        continue

    # losowe proxy
    proxy = random.choice(proxies)
    print(f"\nScrapuję: {url} przez proxy: {proxy}")

    driver = None
    try:
        driver = get_driver(proxy)
        driver.get(url)
        time.sleep(5)  # czekamy na załadowanie JS

        # --- Pobranie AQI (nazwa + liczba) ---
        try:
            aqi_elem = driver.find_element(By.CLASS_NAME, "aqi-value")
            aqi_value = aqi_elem.text.strip()
        except:
            aqi_value = None

        # --- Pobranie pollutantów ---
        pollutants = {}
        try:
            pollutant_elements = driver.find_elements(By.CLASS_NAME, "pollutant-item")
            for p in pollutant_elements:
                try:
                    name = p.find_element(By.CLASS_NAME, "name").text.strip()
                    value = p.find_element(By.CLASS_NAME, "value").text.strip()
                    pollutants[name] = value
                except:
                    continue
        except:
            pass

        # zapis wyniku
        results.append({
            "url": url,
            "proxy_used": proxy,
            "aqi": aqi_value,
            "pollutants": pollutants
        })

        time.sleep(random.uniform(2, 4))

    except Exception as e:
        print("Błąd scrapingu:", e)

    finally:
        if driver:
            driver.quit()


# --- Zapis do JSON ---
with open("aqi_data.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print("\nScraping zakończony. Dane zapisane w aqi_data.json\n")
