from datetime import datetime, timezone

def calculate_uptime(created_time_str):
    created_timestamp = datetime.strptime(created_time_str[:26], "%Y-%m-%dT%H:%M:%S.%f")
    created_timestamp = created_timestamp.replace(tzinfo=timezone.utc)
    uptime = datetime.now(timezone.utc) - created_timestamp
    return str(uptime).split('.')[0]  # Remove microseconds
