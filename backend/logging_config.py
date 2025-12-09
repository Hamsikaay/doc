import logging
import socket
import json
import os
from datetime import datetime

LOGSTASH_HOST = os.getenv("LOGSTASH_HOST", "logstash")
LOGSTASH_PORT = int(os.getenv("LOGSTASH_PORT", "5000"))


class UDPJsonLogstashHandler(logging.Handler):
    """
    Simple UDP handler that sends logs as one-line JSON strings
    to Logstash (listening on udp/5000).
    """
    def __init__(self, host: str, port: int):
        super().__init__()
        self.addr = (host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def emit(self, record: logging.LogRecord):
        try:
            log_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "funcName": record.funcName,
                "lineno": record.lineno,
            }

            data = (json.dumps(log_record) + "\n").encode("utf-8")
            self.socket.sendto(data, self.addr)

        except Exception:
            self.handleError(record)


def configure_logging():
    """
    Attach:
    - Console handler (stdout) for normal viewing
    - UDP JSON handler to Logstash
    """
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Avoid duplicate handlers if called multiple times
    if getattr(root, "_logstash_configured", False):
        return

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    ))

    # Logstash handler
    lh = UDPJsonLogstashHandler(LOGSTASH_HOST, LOGSTASH_PORT)

    root.addHandler(ch)
    root.addHandler(lh)

    root._logstash_configured = True
