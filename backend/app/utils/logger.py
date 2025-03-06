import logging
import watchtower
import boto3
from app.config import settings

# Set up CloudWatch Logs
LOG_GROUP = "MyAppLogs"
LOG_STREAM = "Backend"

# Initialize Logger
logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

# Configure AWS CloudWatch client
cloudwatch_client = boto3.client(
    "logs",
    region_name=settings.aws_region,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key
)

# Add CloudWatch handler
if not any(isinstance(handler, watchtower.CloudWatchLogHandler) for handler in logger.handlers):
    logger.addHandler(watchtower.CloudWatchLogHandler(
        log_group=LOG_GROUP,
        stream_name=LOG_STREAM
    ))

logger.info("CloudWatch logging is set up.")