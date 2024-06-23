from .docker_monitor import DockerMonitor

class MonitorManager:
    def __init__(self, services, notification_manager):
        self.monitors = []
        if 'docker' in services:
            self.monitors.append(DockerMonitor(notification_manager))

    def handle_updates(self):
        # Logic to handle updates (e.g., from Telegram) goes here
        pass
