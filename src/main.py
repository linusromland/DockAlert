from threading import Thread
from config import NOTIFICATION_METHODS, MONITOR_SERVICES
from logging_config import configure_logging
from notifications import NotificationManager
from monitors import MonitorManager

def main():
    configure_logging()

    notification_manager = NotificationManager(NOTIFICATION_METHODS)
    monitor_manager = MonitorManager(MONITOR_SERVICES, notification_manager)

    notification_manager.send_initial_message()

    for monitor in monitor_manager.monitors:
        thread = Thread(target=monitor.run)
        thread.start()

    monitor_manager.handle_updates()

if __name__ == "__main__":
    main()
