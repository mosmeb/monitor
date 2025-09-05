import requests
import os
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
SITES_TO_CHECK = [
    "https://mebelmoscow.ru/",
    "https://mebel-liberty.ru/"
]
TIMEOUT_THRESHOLD = 0.2  # 200 мс

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")
        return False

def check_site(url):
    try:
        start_time = datetime.now()
        response = requests.get(url, timeout=10)
        response_time = (datetime.now() - start_time).total_seconds()
        return {'status': response.status_code, 'response_time': response_time, 'success': True}
    except Exception as e:
        return {'status': str(e), 'response_time': None, 'success': False}

def main():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    for url in SITES_TO_CHECK:
        result = check_site(url)
        
        if not result['success']:
            message = f"🚨 Сайт недоступен\nВремя: {current_time}\nСайт: {url}\nОшибка: {result['status']}"
            send_telegram_alert(message)
        elif result['status'] != 200:
            message = f"⚠️ Ошибка статуса\nВремя: {current_time}\nСайт: {url}\nСтатус: {result['status']}"
            send_telegram_alert(message)
        elif result['response_time'] > TIMEOUT_THRESHOLD:
            message = f"🐌 Медленный ответ\nВремя: {current_time}\nСайт: {url}\nВремя ответа: {result['response_time']:.3f} сек"
            send_telegram_alert(message)
        else:
            print(f"✓ {url} - OK ({result['response_time']:.3f} сек)")

if __name__ == "__main__":
    main()
