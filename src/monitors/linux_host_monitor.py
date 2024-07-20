import os

import paramiko
import logging
from time import sleep
from src.config import RETRY_INTERVAL

class LinuxHostMonitor():
    name = "LinuxHost"

    def __init__(self, notification_manager):
        hosts = os.getenv('HOSTS').split(',') if os.getenv('HOSTS') else []
        if not hosts:
            raise ValueError("Atleast one host must be provided to monitor.")

        for host in hosts:
            self.validate_host(host)

        SSH_KEY_FILEPATH = os.getenv('SSH_KEY_FILEPATH')
        if not SSH_KEY_FILEPATH:
            raise ValueError("SSH_KEY_FILEPATH environment variable must be set.")

        self.hosts = hosts
        self.key_filepath = SSH_KEY_FILEPATH
        self.notification_manager = notification_manager
        self.host_status = {host: None for host in hosts}

    def validate_host(self, host):
        username, hostname = host.split('@')

        if not username or not hostname:
            raise ValueError(f"Invalid host format: {host}")

        logging.info("Host %s is valid. Starting monitor...", host)


    def running(self):
        return True

    def get_ssh_client(self, username, host):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host, username=username, key_filename=self.key_filepath, timeout=5)
            return client
        except paramiko.ssh_exception.AuthenticationException as e:
            logging.error("Authentication error for host %s: %s", host, e)
            return None

    def check_host_status(self, host):
        try:
            client = self.get_ssh_client(host)
            if client is None:
                logging.info("Failed to connect to host %s", host)
                return "offline"

            client.close()
            logging.info("Host %s is online", host)
            return "online"
        except Exception as e:
            logging.error("Failed to check host %s status: %s", host, e)
            return "offline"

    def get_initial_message(self):
        message = "Initial host status:\n"
        for host in self.hosts:
            status = self.check_host_status(host)
            self.host_status[host] = status
            message += f"Host {host}: {status}\n"
        return message

    def monitor_host(self, host):
        while True:
            logging.info("Checking host %s status...", host)
            current_status = self.check_host_status(host)
            if self.host_status[host] != current_status:
                self.host_status[host] = current_status
                message = f"Host {host} status changed to: {current_status}"
                logging.info(message)
                self.notification_manager.send_message(message, self.name)
            sleep(RETRY_INTERVAL)

    def run(self):
        for host in self.hosts:
            self.monitor_host(host)

