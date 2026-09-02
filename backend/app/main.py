import sqlite3
import pickle
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apscheduler.schedulers.background import BackgroundScheduler
from fetch_data import run_fetch_cycle

app = FastAPI(title="SmogWatch API")
scheduler = BackgroundScheduler()
scheduler.add_job(run_fetch_cycle, "interval", hours=1, id="fetch_air_quality")
scheduler.start()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "smogwatch.db"
HORIZON_HOURS = 6

with open("forecast_model.pkl", "rb") as f:
    model = pickle.load(f)

from fetch_data import init_db
init_db()

def get_aqi_label(aqi: int) -> str:
    labels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
    return labels.get(aqi, "Unknown")


@app.get("/")
def read_root():
    return {"status": "SmogWatch API is running"}


@app.get("/current")
def get_current():
    """Latest recorded reading."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM air_quality_readings ORDER BY timestamp DESC LIMIT 1"
    ).fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="No data available yet")

    data = dict(row)
    data["aqi_label"] = get_aqi_label(data["aqi"])
    return data


@app.get("/history")
def get_history(hours: int = 48):
    """Recent readings for charting, default last 48 hours."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT timestamp, aqi, pm2_5, pm10 FROM air_quality_readings "
        "ORDER BY timestamp DESC LIMIT ?",
        (hours,),
    ).fetchall()
    conn.close()

    readings = [dict(r) for r in rows]
    readings.reverse()  # chronological order for charting
    return {"readings": readings}


@app.get("/forecast")
def get_forecast():
    """Predict PM2.5 HORIZON_HOURS from now, using the most recent data."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        "SELECT * FROM air_quality_readings ORDER BY timestamp DESC LIMIT 25",
        conn,
    )
    conn.close()

    if len(df) < 25:
        raise HTTPException(
            status_code=503,
            detail="Not enough historical data yet to generate a forecast.",
        )

    df = df.iloc[::-1].reset_index(drop=True)  # back to chronological order
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="mixed")

    latest = df.iloc[-1]

    features = {
        "pm2_5": latest["pm2_5"],
        "pm10": latest["pm10"],
        "no2": latest["no2"],
        "so2": latest["so2"],
        "co": latest["co"],
        "o3": latest["o3"],
        "hour_sin": np.sin(2 * np.pi * latest["timestamp"].hour / 24),
        "hour_cos": np.cos(2 * np.pi * latest["timestamp"].hour / 24),
        "day_of_week": latest["timestamp"].dayofweek,
        "month": latest["timestamp"].month,
        "pm2_5_lag_1h": df["pm2_5"].iloc[-2] if len(df) >= 2 else latest["pm2_5"],
        "pm2_5_lag_3h": df["pm2_5"].iloc[-4] if len(df) >= 4 else latest["pm2_5"],
        "pm2_5_lag_6h": df["pm2_5"].iloc[-7] if len(df) >= 7 else latest["pm2_5"],
        "pm2_5_lag_12h": df["pm2_5"].iloc[-13] if len(df) >= 13 else latest["pm2_5"],
        "pm2_5_lag_24h": df["pm2_5"].iloc[-25] if len(df) >= 25 else latest["pm2_5"],
        "pm2_5_rolling_6h": df["pm2_5"].iloc[-6:].mean(),
        "pm2_5_rolling_24h": df["pm2_5"].iloc[-24:].mean(),
    }

    X = pd.DataFrame([features])
    prediction = model.predict(X)[0]

    return {
        "current_pm2_5": round(float(latest["pm2_5"]), 2),
        "predicted_pm2_5": round(float(prediction), 2),
        "horizon_hours": HORIZON_HOURS,
        "predicted_at": datetime.now(timezone.utc).isoformat(),
    }