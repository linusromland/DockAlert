import socket
from datetime import datetime

import requests
from .telegram import TelegramNotification

class NotificationManager:
    def __init__(self, methods):
        self.external_ip = None
        self.internal_ip = None
        self.last_ip_check = None
        self.notifiers = []
        self.hostname = socket.gethostname()
        self.getIpAdresses()

        if 'telegram' in methods:
            self.notifiers.append(TelegramNotification())


    def getIpAdresses(self):
        if self.last_ip_check and (datetime.now() - self.last_ip_check).seconds < 7200:
            return self.internal_ip, self.external_ip

        self.last_ip_check = datetime.now()

        self.internal_ip = socket.gethostbyname(self.hostname)

        # Get the external IP
        try:
            response = requests.get('https://api.ipify.org?format=json')
            self.external_ip = response.json()['ip']
        except requests.RequestException:
            self.external_ip = None


    def send_initial_message(self, monitor_initial_messages):
        init_message = "AlertBot monitoring started."
        init_message += "\n" + monitor_initial_messages
        self.send_message(init_message)

    def send_message(self, message):
        self.getIpAdresses()

        formatted_message = f"Hostname:  {self.hostname}"
        formatted_message += f"\nInternal IP: {self.internal_ip}"
        formatted_message += f"\nExternal IP: {self.external_ip}"
        formatted_message += f"\n\n{message}"

        for notifier in self.notifiers:
            notifier.send_message(formatted_message)
