import docker
import logging
from datetime import datetime, timezone
from time import sleep
from config import RETRY_INTERVAL

class DockerMonitor():
    def __init__(self, notification_manager):
        self.notification_manager = notification_manager
        try:
            self.client = docker.from_env()
        except docker.errors.DockerException as e:
            logging.error("Failed to initialize Docker client: %s", e)
            exit(1)

    def run(self):
        while True:
            try:
                for event in self.client.events(decode=True):
                    if event['Type'] == 'container':
                        status = event.get('status', 'unknown')
                        container_name = event['Actor']['Attributes'].get('name', 'unknown')
                        container_id = event['id']
                        container = self.client.containers.get(container_id)
                        image_name = container.attrs['Config']['Image']

                        message = f"Container {container_name} ({image_name}) status changed: {status}"
                        logging.info(message)
                        self.notification_manager.send_message(message)
            except docker.errors.APIError as e:
                logging.error("Docker API error: %s", e)
                logging.info("Retrying in %d seconds...", RETRY_INTERVAL)
                sleep(RETRY_INTERVAL)
            except Exception as e:
                logging.error("Unexpected error: %s", e)
                logging.info("Retrying in %d seconds...", RETRY_INTERVAL)
                sleep(RETRY_INTERVAL)
