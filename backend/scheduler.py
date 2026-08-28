from apscheduler.schedulers.blocking import BlockingScheduler
from fetch_data import run_fetch_cycle

scheduler = BlockingScheduler()

# Run every hour, on the hour
scheduler.add_job(run_fetch_cycle, "interval", hours=1, id="fetch_air_quality")

if __name__ == "__main__":
    print("Scheduler started. Fetching air quality data every hour...")
    run_fetch_cycle()  # run once immediately on startup, don't wait an hour
    scheduler.start()