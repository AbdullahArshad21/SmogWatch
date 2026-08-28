import os
import sqlite3
from datetime import datetime, timezone, timedelta
import requests
import time
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
LAT = 31.5497
LON = 74.3436
DB_PATH = "smogwatch.db"

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
            temp REAL,
            humidity REAL,
            wind_speed REAL,
            fetch_status TEXT DEFAULT 'ok'
        )
    """)
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

def fetch_historical_chunk(start_ts: int, end_ts: int) -> list:
    """Fetch historical readings between two Unix timestamps.
    OpenWeatherMap's history endpoint returns hourly readings for the
    requested range in one call.
    """
    url = (
        f"http://api.openweathermap.org/data/2.5/air_pollution/history"
        f"?lat={LAT}&lon={LON}&start={start_ts}&end={end_ts}&appid={API_KEY}"
    )
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.json()["list"]


def save_readings(readings: list):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    saved_count = 0

    for r in readings:
        timestamp = datetime.fromtimestamp(r["dt"], tz=timezone.utc).isoformat()
        components = r["components"]

        existing = cursor.execute(
            "SELECT id FROM air_quality_readings WHERE timestamp = ?", (timestamp,)
        ).fetchone()
        if existing:
            continue

        cursor.execute("""
            INSERT INTO air_quality_readings
            (timestamp, aqi, pm2_5, pm10, no2, so2, co, o3, temp, humidity, wind_speed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL)
        """, (
            timestamp, r["main"]["aqi"], components["pm2_5"], components["pm10"],
            components["no2"], components["so2"], components["co"], components["o3"],
        ))
        saved_count += 1

    conn.commit()
    conn.close()
    return saved_count


def backfill_historical_data(days_back: int = 90):
    """Pull the last N days of historical data, in weekly chunks (API
    has practical limits on range size per call, so we chunk it).
    """
    init_db()

    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=days_back)

    current = start_time
    total_saved = 0

    while current < end_time:
        chunk_end = min(current + timedelta(days=7), end_time)

        start_ts = int(current.timestamp())
        end_ts = int(chunk_end.timestamp())

        print(f"Fetching {current.date()} to {chunk_end.date()}...")

        try:
            readings = fetch_historical_chunk(start_ts, end_ts)
            saved = save_readings(readings)
            total_saved += saved
            print(f"  -> Saved {saved} new readings")
        except requests.exceptions.RequestException as e:
            print(f"  -> Failed: {e}")

        current = chunk_end
        time.sleep(1)  # be polite to the API, avoid hammering it

    print(f"\nBackfill complete. Total new readings saved: {total_saved}")


if __name__ == "__main__":
    backfill_historical_data(days_back=90)