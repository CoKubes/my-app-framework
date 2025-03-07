import logging
import os
import watchtower
from app.config import settings


# Ensure logs/ directory exists
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Create a logger instance
logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

# Create a file handler for local logs
file_handler = logging.FileHandler("logs/app.log")
file_handler.setLevel(logging.INFO)


# Create a CloudWatch log handler
cloudwatch_handler = watchtower.CloudWatchLogHandler(
    log_group=settings.aws_log_group,
    stream_name=settings.aws_log_stream,
)

# Set log format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
cloudwatch_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(cloudwatch_handler)

logger.info("Logging setup complete!")

