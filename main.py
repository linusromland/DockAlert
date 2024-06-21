"""
Monitor Docker events and send notifications to Telegram on container status changes.
"""
import os
import logging
from time import sleep
import docker
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
RETRY_INTERVAL = os.getenv('RETRY_INTERVAL', '10')

if not BOT_TOKEN or not CHAT_ID:
    logging.error("BOT_TOKEN and CHAT_ID environment variables must be set.")
    exit(1)

try:
    RETRY_INTERVAL = int(RETRY_INTERVAL)
except ValueError as value_error:
    logging.error("RETRY_INTERVAL must be an integer: %s", value_error)
    exit(1)

TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# Initialize Docker client
try:
    client = docker.from_env()
except docker.errors.DockerException as docker_error:
    logging.error("Failed to initialize Docker client: %s", docker_error)
    exit(1)


def send_telegram_message(message):
    """
    Send a message to the specified Telegram chat.

    :param message: The message to send.
    """
    try:
        response = requests.post(TELEGRAM_API_URL, data={"chat_id": CHAT_ID, "text": message}, timeout=10)
        response.raise_for_status()
        logging.info("Message sent: %s", message)
    except requests.exceptions.RequestException as request_error:
        logging.error("Failed to send message: %s", request_error)


def monitor_docker_events():
    """
    Monitor Docker events and send notifications to Telegram on container status changes.
    """
    while True:
        try:
            for event in client.events(decode=True):
                if event['Type'] == 'container':
                    status = event.get('status', 'unknown')
                    container_name = event['Actor']['Attributes'].get('name', 'unknown')
                    message = f"Container {container_name} status changed: {status}"
                    logging.info("Container %s status changed: %s",container_name, status)
                    send_telegram_message(message)
        except docker.errors.APIError as docker_api_error:
            logging.error("Docker API error: %s", docker_api_error)
            logging.info("Retrying in %d seconds...", RETRY_INTERVAL)
            sleep(RETRY_INTERVAL)
        except (docker.errors.DockerException, requests.exceptions.RequestException) as specific_error:
            logging.error("Specific error: %s", specific_error)
            logging.info("Retrying in %d seconds...", RETRY_INTERVAL)
            sleep(RETRY_INTERVAL)
        except Exception as general_error:
            logging.error("Unexpected error: %s", general_error)
            logging.info("Retrying in %d seconds...", RETRY_INTERVAL)
            sleep(RETRY_INTERVAL)


if __name__ == "__main__":
    INIT_MESSAGE = "DockAlert monitoring started."
    logging.info(INIT_MESSAGE)
    send_telegram_message(INIT_MESSAGE)
    monitor_docker_events()
