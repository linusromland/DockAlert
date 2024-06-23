from .telegram import TelegramNotification

class NotificationManager:
    def __init__(self, methods):
        self.notifiers = []
        if 'telegram' in methods:
            self.notifiers.append(TelegramNotification())

    def send_initial_message(self):
        init_message = "AlertBot monitoring started."
        self.send_message(init_message)

    def send_message(self, message):
        for notifier in self.notifiers:
            notifier.send_message(message)
