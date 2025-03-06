import boto3
import os
from app.config import settings

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