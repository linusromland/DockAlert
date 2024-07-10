import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
RETRY_INTERVAL = int(os.getenv('RETRY_INTERVAL', '10'))
NOTIFICATION_METHODS = ['telegram']
MONITOR_SERVICES = ['docker', 'linux_host']

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("BOT_TOKEN and CHAT_ID environment variables must be set.")
