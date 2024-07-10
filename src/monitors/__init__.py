from .docker_monitor import DockerMonitor

class MonitorManager:
    def __init__(self, services, notification_manager):
        self.monitors = []
        if 'docker' in services:
            self.monitors.append(DockerMonitor(notification_manager))

    def get_initial_message(self):
        message = ""
        for monitor in self.monitors:
            message += "\n" + ("-" * 30) + "\n"
            message += f"Service: {monitor.name}"
            is_running = monitor.running()
            message += f"\nRunning: {is_running}"
            message += f"\n\n{monitor.get_initial_message()}"
        return message


    def handle_updates(self):
        # Logic to handle updates (e.g., from Telegram) goes here
        pass
