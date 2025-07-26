import os
import time
import requests
import schedule
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
COINGLASS_API_KEY = os.getenv("COINGLASS_API_KEY")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)

def fetch_coinglass_data():
    url = "https://open-api.coinglass.com/api/pro/v1/futures/openInterest"
    headers = {"coinglassSecret": COINGLASS_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        return data.get("data", [])
    except Exception as e:
        print(f"[ERROR] {e}")
        return []

def analyze_and_notify():
    data = fetch_coinglass_data()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    alerts = []
    for coin in data:
        symbol = coin.get("symbol", "")
        usdt_oi_change = coin.get("USDT", {}).get("openInterestChangeRate", 0)
        if abs(usdt_oi_change) >= 5:
            direction = "🟢 Increase" if usdt_oi_change > 0 else "🔴 Decrease"
            alert = f"{len(alerts)+1}. <b>{symbol}</b> - {direction} in liquidity ({usdt_oi_change}%)"
            alerts.append(alert)
    if alerts:
        message = f"<b>🚨 Liquidity Alert - {now}</b>

" + "\n".join(alerts)
        send_telegram_message(message)

# جدولة التحقق كل 5 دقائق
schedule.every(5).minutes.do(analyze_and_notify)

if __name__ == "__main__":
    print("[INFO] Bot started...")
    analyze_and_notify()
    while True:
        schedule.run_pending()
        time.sleep(1)