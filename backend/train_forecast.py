import sqlite3
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import pickle

DB_PATH = "smogwatch.db"
HORIZON_HOURS = 6


def load_data() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM air_quality_readings ORDER BY timestamp", conn)
    conn.close()

    df["timestamp"] = pd.to_datetime(df["timestamp"], format="mixed")
    df = df.drop_duplicates(subset="timestamp").reset_index(drop=True)
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Build time-based and lag features that help the model learn
    daily/weekly pollution cycles and recent trends.
    """
    df = df.copy()

    # Time-of-day and calendar features - pollution has strong daily
    # cycles (e.g. worse during evening traffic) and weekly cycles
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["month"] = df["timestamp"].dt.month

    # Cyclical encoding - hour 23 and hour 0 are actually "close" in time,
    # but as raw numbers they look far apart. Sin/cos encoding fixes this.
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)

    # Lag features - the single strongest predictor of pollution soon
    # from now is usually pollution right now. We give the model recent
    # history to learn from.
    for lag in [1, 3, 6, 12, 24]:
        df[f"pm2_5_lag_{lag}h"] = df["pm2_5"].shift(lag)

    # Rolling averages - smoothed recent trend, less noisy than a single
    # lag value
    df["pm2_5_rolling_6h"] = df["pm2_5"].rolling(window=6).mean()
    df["pm2_5_rolling_24h"] = df["pm2_5"].rolling(window=24).mean()

    # Target: PM2.5 value HORIZON_HOURS in the future - this is what
    # we're actually trying to predict
    df[f"target_pm2_5_{HORIZON_HOURS}h_ahead"] = df["pm2_5"].shift(-HORIZON_HOURS)

    # Only drop rows missing values in the columns we actually use for
    # training - NOT the whole dataframe. temp/humidity/wind_speed are
    # still empty for most historical rows (weather collection just
    # started), but we don't use them as features yet, so they shouldn't
    # cause us to drop otherwise-good rows.
    required_cols = [
        "pm2_5", "pm10", "no2", "so2", "co", "o3",
        "pm2_5_lag_1h", "pm2_5_lag_3h", "pm2_5_lag_6h", "pm2_5_lag_12h", "pm2_5_lag_24h",
        "pm2_5_rolling_6h", "pm2_5_rolling_24h",
        f"target_pm2_5_{HORIZON_HOURS}h_ahead",
    ]
    df = df.dropna(subset=required_cols).reset_index(drop=True)

    return df


def train_model():
    print("Loading data...")
    df = load_data()
    print(f"Loaded {len(df)} readings")

    print("Engineering features...")
    df = engineer_features(df)
    print(f"After feature engineering: {len(df)} usable rows")

    feature_cols = [
        "pm2_5", "pm10", "no2", "so2", "co", "o3",
        "hour_sin", "hour_cos", "day_of_week", "month",
        "pm2_5_lag_1h", "pm2_5_lag_3h", "pm2_5_lag_6h", "pm2_5_lag_12h", "pm2_5_lag_24h",
        "pm2_5_rolling_6h", "pm2_5_rolling_24h",
    ]

    X = df[feature_cols]
    y = df[f"target_pm2_5_{HORIZON_HOURS}h_ahead"]

    # Time-series split - IMPORTANT: we don't shuffle randomly, we split
    # chronologically. Training on future data to predict the past would
    # be cheating (data leakage) and give a falsely optimistic result.
    split_idx = int(len(df) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")

    model = lgb.LGBMRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=6,
        random_state=42,
        verbose=-1,
    )

    model.fit(X_train, y_train)

    # Evaluate against a naive baseline - "in H hours, PM2.5 will be the
    # same as right now". If our model can't beat this simple baseline,
    # it's not actually adding value.
    predictions = model.predict(X_test)
    naive_baseline = X_test["pm2_5"].values  # just use current value as the "prediction"

    model_mae = mean_absolute_error(y_test, predictions)
    baseline_mae = mean_absolute_error(y_test, naive_baseline)

    model_rmse = np.sqrt(mean_squared_error(y_test, predictions))
    baseline_rmse = np.sqrt(mean_squared_error(y_test, naive_baseline))

    print(f"\n--- Results (predicting PM2.5, {HORIZON_HOURS} hours ahead) ---")
    print(f"Model MAE:    {model_mae:.2f}  |  Naive baseline MAE:    {baseline_mae:.2f}")
    print(f"Model RMSE:   {model_rmse:.2f}  |  Naive baseline RMSE:   {baseline_rmse:.2f}")

    if model_mae < baseline_mae:
        improvement = (1 - model_mae / baseline_mae) * 100
        print(f"\nModel beats the naive baseline by {improvement:.1f}%")
    else:
        print(f"\nWarning: model did not beat the naive baseline. Needs more work.")

    # Feature importance - which factors matter most for the prediction
    importance = pd.DataFrame({
        "feature": feature_cols,
        "importance": model.feature_importances_,
    }).sort_values("importance", ascending=False)
    print(f"\nTop 5 most important features:")
    print(importance.head(5).to_string(index=False))

    # Save the trained model
    with open("forecast_model.pkl", "wb") as f:
        pickle.dump(model, f)
    print(f"\nModel saved as forecast_model.pkl (horizon: {HORIZON_HOURS}h)")


if __name__ == "__main__":
    train_model()