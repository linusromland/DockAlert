import requests
import logging
from config import BOT_TOKEN, CHAT_ID

TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

class TelegramNotification():
    def send_message(self, message):
        try:
            response = requests.post(TELEGRAM_API_URL, data={"chat_id": CHAT_ID, "text": message})
            response.raise_for_status()
            logging.info("Message sent: %s", message)
        except requests.exceptions.RequestException as e:
            logging.error("Failed to send message: %s", e)
