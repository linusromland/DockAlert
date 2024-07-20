import requests
import logging
import os


class TelegramNotification():


    def __init__(self):
        BOT_TOKEN: str | None = os.getenv('TELEGRAM_BOT_TOKEN')
        CHAT_ID: str | None = os.getenv('TELEGRAM_CHAT_ID')

        if not BOT_TOKEN or not CHAT_ID:
            raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables must be set.")

        self.TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        self.CHAT_ID = CHAT_ID

    def send_message(self, message):
        try:
            response = requests.post(self.TELEGRAM_API_URL, data={"chat_id": self.CHAT_ID, "text": message})
            response.raise_for_status()
            logging.info("Message sent: %s", message)
        except requests.exceptions.RequestException as e:
            logging.error("Failed to send message: %s", e)
