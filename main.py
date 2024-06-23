import os
import docker
import requests
import logging
from time import sleep
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        response = requests.post(TELEGRAM_API_URL, data={"chat_id": CHAT_ID, "text": message})
        response.raise_for_status()
        logging.info("Message sent: %s", message)
    except requests.exceptions.RequestException as request_error:
        logging.error("Failed to send message: %s", request_error)

def get_all_containers_info():
    """
    Retrieve information about all Docker containers (running and stopped).

    :return: A formatted string with container information.
    """
    try:
        containers = client.containers.list(all=True)
        if not containers:
            return "No containers found."

        info_message = "All containers:\n"
        for container in containers:
            status = container.status
            container_name = container.name
            created_time = container.attrs['Created']  # Get creation time as string
            created_timestamp = datetime.strptime(created_time[:26], "%Y-%m-%dT%H:%M:%S.%f")  # Parse datetime
            created_timestamp = created_timestamp.replace(tzinfo=timezone.utc)  # Ensure UTC timezone
            uptime = datetime.now(timezone.utc) - created_timestamp
            uptime_str = str(uptime).split('.')[0]  # Remove microseconds

            image_name = container.attrs['Config']['Image']  # Get Docker image name
            info_message += f"- {container_name} ({image_name}): Status {status}, Uptime {uptime_str}\n"

        return info_message
    except docker.errors.APIError as api_error:
        logging.error("Failed to fetch Docker containers: %s", api_error)
        return "Failed to fetch Docker containers information."

def get_running_containers_info():
    """
    Retrieve information about all running Docker containers.

    :return: A formatted string with running container information.
    """
    try:
        containers = client.containers.list()
        if not containers:
            return "No running containers found."

        info_message = "Running containers:\n"
        for container in containers:
            status = container.status
            container_name = container.name
            created_time = container.attrs['Created']  # Get creation time as string
            created_timestamp = datetime.strptime(created_time[:26], "%Y-%m-%dT%H:%M:%S.%f")  # Parse datetime
            created_timestamp = created_timestamp.replace(tzinfo=timezone.utc)  # Ensure UTC timezone
            uptime = datetime.now(timezone.utc) - created_timestamp
            uptime_str = str(uptime).split('.')[0]  # Remove microseconds

            image_name = container.attrs['Config']['Image']  # Get Docker image name
            info_message += f"- {container_name} ({image_name}): Status {status}, Uptime {uptime_str}\n"

        return info_message
    except docker.errors.APIError as api_error:
        logging.error("Failed to fetch running Docker containers: %s", api_error)
        return "Failed to fetch running Docker containers information."

def handle_telegram_updates():
    """
    Continuously poll for new messages from Telegram and handle commands.
    """
    last_update_id = None
    while True:
        try:
            params = {'timeout': 100, 'allowed_updates': ['message']}
            if last_update_id:
                params['offset'] = last_update_id + 1

            response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates", params=params)
            response.raise_for_status()
            updates = response.json().get('result', [])

            for update in updates:
                message = update.get('message')
                if not message:
                    continue

                chat_id = message['chat']['id']
                text = message.get('text', '').strip().lower()

                if chat_id != int(CHAT_ID):
                    continue

                if text == '/list':
                    running_containers_info = get_running_containers_info()
                    send_telegram_message(running_containers_info)
                elif text == '/all':
                    all_containers_info = get_all_containers_info()
                    send_telegram_message(all_containers_info)
                elif text == '/help':
                    help_message = "Available commands:\n"
                    help_message += "/list - List running containers\n"
                    help_message += "/all - List all containers\n"
                    send_telegram_message(help_message)

                last_update_id = update['update_id']

            sleep(1)
        except requests.exceptions.RequestException as request_error:
            logging.error("Failed to fetch Telegram updates: %s", request_error)
            sleep(RETRY_INTERVAL)
        except Exception as general_error:
            logging.error("Unexpected error: %s", general_error)
            sleep(RETRY_INTERVAL)

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
                    container_id = event['id']
                    container = client.containers.get(container_id)
                    image_name = container.attrs['Config']['Image']

                    message = f"Container {container_name} ({image_name}) status changed: {status}"
                    logging.info("Container %s status changed: %s", container_name, status)
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
    INIT_MESSAGE = "DockAlert monitoring started.\n\n"
    INIT_MESSAGE += get_all_containers_info()
    logging.info(INIT_MESSAGE)
    send_telegram_message(INIT_MESSAGE)

    from threading import Thread
    # Start Docker event monitoring in a separate thread
    docker_thread = Thread(target=monitor_docker_events)
    docker_thread.start()

    # Handle Telegram updates in the main thread
    handle_telegram_updates()
