import requests
import schedule
import time
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
COINGLASS_API_KEY = os.getenv("COINGLASS_API_KEY")

last_alerts = {}

def get_coin_glass_data():
    url = "https://open-api.coinglass.com/public/v2/futures/longShortChart"
    headers = {"coinglassSecret": COINGLASS_API_KEY}
    params = {"symbol": "BTC", "interval": "60"}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    return data.get("data", [])

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)

def analyze_and_alert():
    global last_alerts
    data = get_coin_glass_data()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not data:
        return

    alerts = []
    for item in data:
        symbol = item.get("symbol", "N/A")
        long_ratio = float(item.get("longAccount", 0))
        short_ratio = float(item.get("shortAccount", 0))
        ratio = abs(long_ratio - short_ratio)
        direction = "Long" if long_ratio > short_ratio else "Short"

        if ratio >= 5:
            alert_id = f"{symbol}_{direction}_{now[:10]}"
            if alert_id not in last_alerts:
                last_alerts[alert_id] = 1
            else:
                last_alerts[alert_id] += 1

            alerts.append(f"{len(alerts)+1}. <b>{symbol}</b>: {direction} bias with <b>{ratio:.2f}%</b> difference.")

    if alerts:
        message = f"<b>🚨 Liquidity Alert - {now}</b>\n" + "\n".join(alerts)
        send_telegram_message(message)

def main():
    analyze_and_alert()
    schedule.every(5).minutes.do(analyze_and_alert)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()