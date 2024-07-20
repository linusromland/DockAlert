import os
from dotenv import load_dotenv

load_dotenv()

RETRY_INTERVAL = int(os.getenv('RETRY_INTERVAL', '10'))

NOTIFICATION_METHODS_FROM_CONFIG = os.getenv('NOTIFICATION_METHODS')
ALLOWED_NOTIFICATION_METHODS = ['telegram']
NOTIFICATION_METHODS = NOTIFICATION_METHODS_FROM_CONFIG.split(',') if NOTIFICATION_METHODS_FROM_CONFIG else []

# Check that the length of NOTIFICATION_METHODS is not 0
if not NOTIFICATION_METHODS:
    raise ValueError("Atleast one notification method must be provided. Allowed methods are: {ALLOWED_NOTIFICATION_METHODS}")

for method in NOTIFICATION_METHODS:
    if method not in ALLOWED_NOTIFICATION_METHODS:
        raise ValueError(f"{method} is not an allowed notification method. Allowed methods are: {ALLOWED_NOTIFICATION_METHODS}")

MONITOR_SERVICES_FROM_CONFIG = os.getenv('MONITOR_SERVICES')
ALLOWED_MONITOR_SERVICES = ['docker', 'linux_host']
MONITOR_SERVICES = MONITOR_SERVICES_FROM_CONFIG.split(',') if MONITOR_SERVICES_FROM_CONFIG else []

if not MONITOR_SERVICES:
    raise ValueError("Atleast one service must be provided to monitor. Allowed services are: {ALLOWED_MONITOR_SERVICES}")

for service in MONITOR_SERVICES:
    if service not in ALLOWED_MONITOR_SERVICES:
        raise ValueError(f"{service} is not an allowed service to monitor. Allowed services are: {ALLOWED_MONITOR_SERVICES}")

