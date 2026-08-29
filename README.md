# SmogWatch

Live air quality monitoring and forecasting for Lahore, Pakistan.

## Why this project

Lahore is consistently ranked among the most polluted cities in the world, especially during smog season (Oct-Feb). This project collects real air quality data hourly and forecasts PM2.5 levels 6 hours ahead, so people can plan around worsening conditions before they happen.

## How it works

- A scheduled background job fetches live air quality + weather data from OpenWeatherMap every hour
- A LightGBM model, trained on real historical readings, forecasts PM2.5 levels 6 hours ahead
- Model performance is evaluated against a naive baseline ("assume no change"), not just raw accuracy — an honest check for whether the model adds real value
- FastAPI serves current conditions, recent history, and forecasts

## Current model performance

Trained on ~90 days of summer 2026 data (2,113 hourly readings). At a 6-hour forecast horizon, the model beats a naive baseline by a modest margin. This is expected — pollution changes relatively slowly hour-to-hour under stable conditions, which is most of what the model has seen so far.

The live data pipeline keeps running and collecting real data through Lahore's smog season (Oct-Feb), when pollution levels swing far more dramatically. The plan is to retrain with this higher-variance data, and with weather features (wind speed, humidity) fully included, both of which should meaningfully improve forecasting power.

## Tech stack

**Backend:** FastAPI, LightGBM, SQLite, APScheduler
**Frontend:** Next.js, TypeScript, Tailwind CSS

## Status

Actively collecting data. Frontend dashboard and deployment in progress.