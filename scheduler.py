import schedule
import time
import subprocess
import datetime
import os

def run_daily_pipeline():
    print(f"\n[{datetime.datetime.now()}] 🔄 Starting Daily Pipeline...")
    
    # 1. Fetch new data
    try:
        print(f"[{datetime.datetime.now()}] 📡 Running news_fetcher.py")
        subprocess.run([r".venv\Scripts\python", "news_fetcher.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running news_fetcher.py: {e}")
        return

    # 2. Retrain Model
    try:
        print(f"[{datetime.datetime.now()}] 🧠 Running distilbert_classifier.py to update model")
        subprocess.run([r".venv\Scripts\python", "distilbert_classifier.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running distilbert_classifier.py: {e}")

# Run once immediately, then schedule daily
run_daily_pipeline()

schedule.every().day.at("02:00").do(run_daily_pipeline)

print("📅 Scheduler started. Running daily at 02:00 AM.")
while True:
    schedule.run_pending()
    time.sleep(60)
