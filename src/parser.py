import re
from datetime import datetime

LOG_PATTERN = re.compile(
    r"(?P<date>\d{6})\s+"
    r"(?P<time>\d{6})\s+"
    r"\d+\s+"
    r"(?P<level>INFO|WARN|ERROR)\s+"
    r"(?P<component>[^:]+):\s+"
    r"(?P<message>.*)"
)

def parse_log_line(log_line):
    match = LOG_PATTERN.match(log_line)
    if not match:
        return None

    data = match.groupdict()

    # Convert HDFS date+time → datetime
    event_time = datetime.strptime(
        data["date"] + data["time"], "%m%d%y%H%M%S"
    )

    return {
        "event_time": event_time,
        "log_level": data["level"],
        "component": data["component"],
        "message": data["message"]
    }

