from datetime import datetime, timedelta
from models.event import Event
from botocore.exceptions import ClientError
from decimal import Decimal
import boto3
import uuid
import logging
import json

logger = logging.getLogger(__name__)


class DeclinedEvents:
    """Store declined events in database"""

    def __init__(self, resource=None, table=None):
        self.db = resource or boto3.resource("dynamodb")
        self.table = table or self.db.Table("Declined")

    def add(self, event: Event):
        # Event -> json -> dict
        # Uses json.loads parser to convert float to decimal (required for Dynamodb)
        e = json.loads(event.model_dump_json(), parse_float=Decimal)

        # expiry used with Dynamo's Time to Live (TTL) which auto deletes expired entries
        expiry = int((datetime.now() + timedelta(days=5)).timestamp())

        logger.info("📡 Writing entry to db")

        try:
            # Must use unique ID as the default event id (event.id_) uses the email id
            # from which it was extracted, which causes conflicts when multiple events
            # are extracted from a single email
            unique_id = str(uuid.uuid4())

            self.table.put_item(
                Item={
                    "id": unique_id,
                    "expiry": expiry,
                    **e,
                }
            )
            return unique_id
        except ClientError as err:
            # DB expections must raise as persistence is necessary to avoid replicating previous events
            logger.error(
                "⚠️ Couldn't add event %s to table %s. Here's why: %s: %s",
                event,
                self.table,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

    def get_all(self):
        logger.info("📡 Getting events from db")

        try:
            response = self.table.scan()
            items = response.get("Items", [])

            logger.info(f"✅ Found {len(items)} events in db")

            return items
        except ClientError as err:
            logger.error(
                "⚠️ Couldn't get events from table %s. Here's why: %s: %s",
                self.table,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )

    # TODO: Unused method
    def get(self, id):
        logger.info("📡 Fetching db entry")
        try:
            response = self.table.get_item(Key={"id": id})
            return response
        except ClientError as err:
            logger.error(
                "⚠️ Couldn't get event %s from table %s. Here's why: %s: %s",
                id,
                self.table,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )

    def delete(self, id) -> dict | None:
        logger.info("📡 Deleting db entry")

        try:
            response = self.table.delete_item(Key={"id": id})
            return response
        except ClientError as err:
            logger.error(
                "⚠️ Couldn't delete event %s from table %s. Here's why: %s: %s",
                id,
                self.table,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
