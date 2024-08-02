# DockAlert

DockAlert is a Python application designed to monitor Docker container events and send notifications to a Telegram chat. It provides real-time updates on container statuses and their uptime.

## Features

Monitors Docker container events.
Sends notifications to a Telegram chat on status changes.
Retrieves and displays information about all Docker containers.

## Setup Guide

### Prerequisites
- Python 3.x installed on your system.
- Docker installed and running.
- Telegram Bot Token and Chat ID for sending notifications.

### Installation
Clone the repository:

```bash
git clone https://github.com/linusromland/DockAlert.git
cd DockAlert
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Run using docker with the following command:
```bash
docker run -d \
  --privileged \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e ENV_VAR1=value1 \
  ghcr.io/linusromland/dockalert:latest
```

Change the ENV_VAR1 to all the vars needed, read more about this below.

### Configuration
Environment Variables:

Create a .env file in the project root directory and provide the following variables:

```
NOTIFICATION_METHODS=<your_notification_services> # Comma separated list of notification services. Supported are: "telegram"
MONITOR_SERVICES=<your_monitor_services> # Comma separated list of services to monitor. Supported are: "docker","linux_host"

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=<your_telegram_bot_token>
TELEGRAM_CHAT_ID=<your_telegram_chat_id>

# Linux host configuration
HOSTS=<your_hosts> # Comma separated list of hosts to monitor. HOST@IP
SSH_KEY_FILEPATH=<your_ssh_key_filepath> # Path to the SSH private key file

RETRY_INTERVAL=10  # Optional: Retry interval in seconds (default is 10)
```

### Start the application:

Run the Python script to start monitoring Docker events:

```bash
python src/main.py
```

## Usage
Upon starting, DockAlert will fetch initial container information and send it to the configured Telegram chat.
It will then continuously monitor Docker events and send notifications for any status changes (e.g., container start, stop, etc.).

## License
This project is licensed under the MIT License. See the `LICENSE` file for more details.
