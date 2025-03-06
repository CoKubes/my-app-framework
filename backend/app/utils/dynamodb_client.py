import boto3
import os
import json
from decimal import Decimal
from app.config import settings
from app.utils.logger import logger

#AWS DynamoDB Client
dynamodb = boto3.resource(
    "dynamodb",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

TABLE_NAME = "Items"

table = dynamodb.Table(TABLE_NAME)

def add_item(item_id: int):
    table.put_item(Item=item_id)

def get_item(item_id: int):
    response = table.get_item(Key={"id": item_id})
    return response.get("Item")

def update_item(item_id: int, updated_data: dict):
    logger.info(f"Updating item in DynamoDB: {item_id}")

    if not updated_data:
        logger.error(f"No valid update data provided for item {item_id}")
        raise ValueError("No update data provided")

    # Remove `id` from update data (cannot modify primary key)
    updated_data.pop("id", None)

    # Generate update expressions
    update_expression = ", ".join(f"#{k} = :{k}" for k in updated_data.keys())
    expression_names = {f"#{k}": k for k in updated_data.keys()}
    expression_values = {
        f":{k}": (v if not isinstance(v, float) else Decimal(str(v))) for k, v in updated_data.items()
    }

    if not expression_values:
        logger.warning(f"No valid attributes to update for item {item_id}")
        raise ValueError("No valid attributes to update")

    # Perform update in DynamoDB
    table.update_item(
        Key={"id": item_id},  
        UpdateExpression=f"SET {update_expression}",
        ExpressionAttributeNames=expression_names,
        ExpressionAttributeValues=expression_values
    )

    logger.info(f"Item {item_id} successfully updated in DynamoDB")