import logging
import os
import json
import watchtower
from app.config import settings
from aws_xray_sdk.core import xray_recorder
from pythonjsonlogger import jsonlogger


# Ensure logs/ directory exists
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Override all Uvicorn loggers
for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    logger.handlers = []  # Clear default handlers
    logger.propagate = False  # Stop propagation to root

# Create a file handler for local logs
file_handler = logging.FileHandler("logs/app.log")
file_handler.setLevel(logging.INFO)


# Create a CloudWatch log handler
cloudwatch_handler = watchtower.CloudWatchLogHandler(
    log_group=settings.aws_log_group,
    stream_name=settings.aws_log_stream,
)

# Use JSON Formatter for logs
formatter = jsonlogger.JsonFormatter(
    fmt="%(asctime)s %(levelname)s %(message)s %(trace_id)s %(span_id)s"
)
file_handler.setFormatter(formatter)
cloudwatch_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(cloudwatch_handler)

logger.info("Logging setup complete!")

# Function to log messages with trace_id and span_id
def log_event(level, message, extra=None):
    segment = xray_recorder.current_segment()
    
    log_data = {
        "trace_id": segment.trace_id if segment else "NO_TRACE",
        "span_id": segment.id if segment else "NO_SPAN",
    }

    if extra:
        log_data.update(extra)

    if level == "info":
        logger.info(message, extra=log_data)
    elif level == "warning":
        logger.warning(message, extra=log_data)
    elif level == "error":
        logger.error(message, extra=log_data)