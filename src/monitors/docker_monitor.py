import docker
import logging
from time import sleep
from src.config import RETRY_INTERVAL

class DockerMonitor():
    name = "Docker"

    def __init__(self, notification_manager):
        self.notification_manager = notification_manager
        try:
            self.client = docker.from_env()
            logging.info("Connected to Docker daemon. Monitoring containers...")
        except docker.errors.DockerException as e:
            if "Connection refused" in str(e):
                logging.info("Docker daemon is not running. Skipping Docker monitor.")
            else:
                logging.error("Failed to connect to Docker daemon: %s", e)
                exit(1)

    def running(self):
        return self.client.ping()

    def get_initial_message(self):
        containers = self.client.containers.list(all=True)
        message = "Initial container status:\n"
        for container in containers:
            container_name = container.name
            container_id = container.id
            status = container.status
            image_name = container.attrs['Config']['Image']
            message += f"Container {container_name} ({image_name}): {status}\n"

        if not containers:
            message += "No containers found."
        return message

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
                        self.notification_manager.send_message(message, self.name)
            except docker.errors.APIError as e:
                logging.error("Docker API error: %s", e)
                logging.info("Retrying in %d seconds...", RETRY_INTERVAL)
                sleep(RETRY_INTERVAL)
            except Exception as e:
                logging.error("Unexpected error: %s", e)
                logging.info("Retrying in %d seconds...", RETRY_INTERVAL)
                sleep(RETRY_INTERVAL)
