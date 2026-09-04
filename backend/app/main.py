import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pickle
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import psycopg2
import psycopg2.extras
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from fetch_data import init_db, run_fetch_cycle
init_db()

app = FastAPI(title="SmogWatch API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")
HORIZON_HOURS = 6


def get_connection():
    return psycopg2.connect(DATABASE_URL)


with open("forecast_model.pkl", "rb") as f:
    model = pickle.load(f)

from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()
scheduler.add_job(run_fetch_cycle, "interval", hours=1, id="fetch_air_quality")
scheduler.start()
run_fetch_cycle()


def get_aqi_label(aqi: int) -> str:
    labels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
    return labels.get(aqi, "Unknown")


@app.get("/")
def read_root():
    return {"status": "SmogWatch API is running"}


@app.get("/current")
def get_current():
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        "SELECT * FROM air_quality_readings ORDER BY timestamp DESC LIMIT 1"
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="No data available yet")

    data = dict(row)
    data["aqi_label"] = get_aqi_label(data["aqi"])
    data["timestamp"] = data["timestamp"].isoformat()
    return data


@app.get("/history")
def get_history(hours: int = 48):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        "SELECT timestamp, aqi, pm2_5, pm10 FROM air_quality_readings "
        "ORDER BY timestamp DESC LIMIT %s",
        (hours,),
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    readings = [dict(r) for r in rows]
    for r in readings:
        r["timestamp"] = r["timestamp"].isoformat()
    readings.reverse()
    return {"readings": readings}


@app.get("/forecast")
def get_forecast():
    conn = get_connection()
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

    df = df.iloc[::-1].reset_index(drop=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

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