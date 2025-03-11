import boto3
import os
import json
from decimal import Decimal
from app.config import settings
from app.utils.logger import log_event
from aws_xray_sdk.core import xray_recorder

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
    with xray_recorder.in_subsegment("DynamoDB GetItem") as subsegment:
        subsegment.put_annotation("item_id", item_id)
        subsegment.put_metadata("operation", "get_item")

        response = table.get_item(Key={"id": item_id})
        item = response.get("Item")

    return item

def update_item(item_id: int, updated_data: dict):
    with xray_recorder.in_subsegment("DynamoDB UpdateItem") as subsegment:
        subsegment.put_annotation("item_id", item_id)
        subsegment.put_metadata("update_data", updated_data)

        # Reserved keyword handling: Replace "name" with a placeholder
        expression_attribute_names = {}
        update_expression = "SET " + ", ".join(f"#{k} = :{k}" for k in updated_data.keys())
        
        for k in updated_data.keys():
            if k.lower() == "name":  # Check if "name" is in the data
                expression_attribute_names["#name"] = "name"
            else:
                expression_attribute_names[f"#{k}"] = k
        
        expression_values = {f":{k}": v for k, v in updated_data.items()}

        table.update_item(
            Key={"id": item_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ExpressionAttributeNames=expression_attribute_names,  
        )
  

def delete_item_from_db(item_id: int):
    with xray_recorder.in_subsegment("DynamoDB DeleteItem") as subsegment:
        subsegment.put_annotation("item_id", item_id)
        table.delete_item(Key={"id": item_id})
    log_event("info", f"Item {item_id} removed from DynamoDB")