import boto3
from app.config import settings
from app.utils.logger import log_event

# Initialize CloudWatch client
cloudwatch = boto3.client(
    "cloudwatch",
    region_name=settings.aws_region
)

def send_cloudwatch_metric(metric_name: str, value: int = 1, unit: str = "Count"):
    """Send a custom metric to AWS CloudWatch."""
    try:
        cloudwatch.put_metric_data(
            Namespace="MyAppMetrics",
            MetricData=[
                {
                    "MetricName": metric_name,
                    "Value": value,
                    "Unit": unit
                }
            ]
        )
        log_event("info", f"Sent metric {metric_name} with value {value} to CloudWatch.")
    except Exception as e:
        log_event("error", f"Failed to send metric {metric_name}: {e}")
