import os
import sqlite3
import time
from datetime import datetime, timezone
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
LAT = 31.5497
LON = 74.3436
DB_PATH = "smogwatch.db"

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS air_quality_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            aqi INTEGER,
            pm2_5 REAL,
            pm10 REAL,
            no2 REAL,
            so2 REAL,
            co REAL,
            o3 REAL,
            fetch_status TEXT DEFAULT 'ok'
        )
    """)
    # A small log table so we can see if the job silently stopped running
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fetch_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            success INTEGER NOT NULL,
            error_message TEXT
        )
    """)
    conn.commit()
    conn.close()


def is_reading_valid(components: dict) -> bool:
    """Basic sanity checks - real air quality values should never be
    negative or absurdly high. This catches corrupted/garbage API
    responses before they pollute our dataset.
    """
    for key, value in components.items():
        if value is None or value < 0 or value > 5000:
            return False
    return True

def fetch_current_air_quality() -> dict | None:
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={LAT}&lon={LON}&appid={API_KEY}"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            reading = data["list"][0]
            components = reading["components"]

            if not is_reading_valid(components):
                log_fetch_result(success=False, error_message="Invalid/out-of-range values in API response")
                return None

            weather = fetch_current_weather() or {"temp": None, "humidity": None, "wind_speed": None}

            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "aqi": reading["main"]["aqi"],
                "pm2_5": components["pm2_5"],
                "pm10": components["pm10"],
                "no2": components["no2"],
                "so2": components["so2"],
                "co": components["co"],
                "o3": components["o3"],
                "temp": weather["temp"],
                "humidity": weather["humidity"],
                "wind_speed": weather["wind_speed"],
            }

        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                log_fetch_result(success=False, error_message=str(e))
                return None

def fetch_current_weather() -> dict | None:
    """Fetch current weather conditions - wind speed and humidity are
    known to significantly affect how pollution disperses.
    """
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            "temp": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
        }
    except requests.exceptions.RequestException as e:
        print(f"Weather fetch failed: {e}")
        return None


def save_reading(reading: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO air_quality_readings
        (timestamp, aqi, pm2_5, pm10, no2, so2, co, o3)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        reading["timestamp"], reading["aqi"], reading["pm2_5"],
        reading["pm10"], reading["no2"], reading["so2"],
        reading["co"], reading["o3"],
    ))
    conn.commit()
    conn.close()
    log_fetch_result(success=True)


def log_fetch_result(success: bool, error_message: str = None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO fetch_log (timestamp, success, error_message)
        VALUES (?, ?, ?)
    """, (datetime.now(timezone.utc).isoformat(), int(success), error_message))
    conn.commit()
    conn.close()


def run_fetch_cycle():
    """One full fetch-and-store cycle - this is what the scheduler will
    call repeatedly.
    """
    reading = fetch_current_air_quality()
    if reading:
        save_reading(reading)
        print(f"[{reading['timestamp']}] Saved reading - AQI: {reading['aqi']}, PM2.5: {reading['pm2_5']}")
    else:
        print("Fetch cycle failed after retries - logged, will try again next cycle.")


if __name__ == "__main__":
    init_db()
    run_fetch_cycle()