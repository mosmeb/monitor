import requests
import os
from datetime import datetime
import sys

# Принудительный вывод
sys.stdout.flush()

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
SITES_TO_CHECK = [
    "https://mebelmoscow.ru/",
    "https://mebel-liberty.ru/"
]

def is_night_time():
    """Проверяем, ночное ли время сейчас по Москве (01:00-08:00)"""
    moscow_time = datetime.utcnow().hour + 3
    if moscow_time >= 24:
        moscow_time -= 24
    return 1 <= moscow_time < 8

def send_telegram_alert(message):
    """Отправка уведомления в Telegram"""
    if is_night_time():
        print("Ночное время - уведомление не отправляется")
        sys.stdout.flush()
        return False
        
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
        sys.stdout.flush()
        return False

def check_site(url):
    """Проверка сайта"""
    try:
        response = requests.get(url, timeout=10)
        return {
            'status': response.status_code,
            'success': True
        }
    except Exception as e:
        return {
            'status': str(e),
            'success': False
        }

def main():
    """Основная функция мониторинга - однократная проверка"""
    if is_night_time():
        print("Ночное время - проверка пропускается")
        sys.stdout.flush()
        return
        
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"Проверка сайтов в {current_time}")
    sys.stdout.flush()
    
    for url in SITES_TO_CHECK:
        result = check_site(url)
        
        if not result['success']:
            message = f"🚨 Сайт недоступен\nВремя: {current_time}\nСайт: {url}\nОшибка: {result['status']}"
            print(message)
            sys.stdout.flush()
            send_telegram_alert(message)
        elif result['status'] != 200:
            message = f"⚠️ Ошибка статуса\nВремя: {current_time}\nСайт: {url}\nСтатус: {result['status']}"
            print(message)
            sys.stdout.flush()
            send_telegram_alert(message)
        else:
            print(f"✓ {url} - OK")
            sys.stdout.flush()
    
    print("Проверка завершена")
    sys.stdout.flush()

if __name__ == "__main__":
    main()
