import requests
import os
from datetime import datetime
import time

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
SITES_TO_CHECK = [
    "https://mebelmoscow.ru/",
    "https://mebel-liberty.ru/"
]

def is_night_time():
    """Проверяем, ночное ли время сейчас по Москве (01:00-08:00)"""
    moscow_time = datetime.utcnow().hour + 3  # UTC+3 для Москвы
    if moscow_time >= 24:
        moscow_time -= 24
    return 1 <= moscow_time < 8  # С 01:00 до 08:00 по Москве

def send_telegram_alert(message):
    """Отправка уведомления в Telegram"""
    if is_night_time():
        print("Ночное время - уведомление не отправляется")
        return False
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        print(f"Попытка отправки сообщения в Telegram: {message}")
        response = requests.post(url, json=payload, timeout=10)
        print(f"Ответ Telegram: {response.status_code} - {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")
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

def send_test_message():
    """Отправка тестового сообщения для отладки"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    test_message = f"🔧 Тестовое сообщение\nВремя: {current_time}\nПроверка работы системы мониторинга"
    print(f"Отправка тестового сообщения: {test_message}")
    return send_telegram_alert(test_message)

def main():
    """Основная функция мониторинга - однократная проверка"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"Проверка сайтов в {current_time}")
    
    # Отправляем тестовое сообщение (можно закомментировать после отладки)
    send_test_message()
    
    for url in SITES_TO_CHECK:
        result = check_site(url)
        
        if not result['success']:
            message = f"🚨 Сайт недоступен\nВремя: {current_time}\nСайт: {url}\nОшибка: {result['status']}"
            print(message)
            send_telegram_alert(message)
        elif result['status'] != 200:
            message = f"⚠️ Ошибка статуса\nВремя: {current_time}\nСайт: {url}\nСтатус: {result['status']}"
            print(message)
            send_telegram_alert(message)
        else:
            print(f"✓ {url} - OK")
    
    print("Проверка завершена")

if __name__ == "__main__":
    main()
