from datetime import datetime, timedelta
from json.decoder import JSONDecodeError
import boto3
from models.event import Event
from botocore.exceptions import ClientError
import logging
import json
from decimal import Decimal

logger = logging.getLogger(__name__)


class Declined:
    """Persist declined events to AWS Dynamodb"""

    def __init__(self, resource=None, table=None):
        self.db = resource or boto3.resource("dynamodb")
        self.table = table or self.db.Table("Declined")

    def add(self, event: Event):
        # Event -> json -> dict
        # Uses json.loads parser to convert float to decimal (required for Dynamodb)
        e = json.loads(event.model_dump_json(), parse_float=Decimal)

        # expiry used with Dynamo's Time to Live (TTL) which auto deletes expired entries
        expiry = int((datetime.now() + timedelta(days=5)).timestamp())

        try:
            self.table.put_item(
                Item={
                    "id": e["id_"],
                    "expiry": expiry,
                    **e,
                }
            )
        except ClientError as err:
            logger.error(
                "⚠️ Couldn't add event %s to table %s. Here's why: %s: %s",
                event,
                self.table,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

    def get_all(self):
        try:
            response = self.table.scan()
            items = response.get("Items", [])
            return items
        except ClientError as err:
            logger.error(
                "⚠️ Couldn't get events from table %s. Here's why: %s: %s",
                self.table,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

    def delete(self, id):
        try:
            self.table.delete_item(Key={"id": id})
        except ClientError as err:
            logger.error(
                "⚠️ Couldn't delete event %s from table %s. Here's why: %s: %s",
                id,
                self.table,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
