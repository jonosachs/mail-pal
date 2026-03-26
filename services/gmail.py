from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from services.credentials import get_credentials
from config import load_secrets
from bs4 import BeautifulSoup
import base64
import logging

logger = logging.getLogger(__name__)


class Gmail:
    def __init__(self):
        self.secrets = load_secrets()
        self.creds = get_credentials()
        self.service = build("gmail", "v1", credentials=self.creds)

    def get_mail(self, filter: str = None, max_results: int = 10):
        """Filters: https://support.google.com/mail/answer/7190"""

        # Get comma separated mailboxes to include in search
        mailboxes = self.secrets["MAILBOXES"].split(",")
        query = " OR ".join([f"in:{m}" for m in mailboxes])
        # Add custom filter arguments if provided
        if filter:
            query += f" {filter}"

        try:
            logger.info("Calling Gmail API..")
            results = (
                # Query params for list:
                # https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list
                self.service.users()
                .messages()
                .list(
                    userId="me",
                    q=query,
                    maxResults=max_results,
                )
                .execute()
            )
            msgs_by_id = results.get("messages", [])

            if not msgs_by_id:
                logger.info(f"No messages found matching query: {query}.")
                return []

            messages = []
            for msg in msgs_by_id:
                msg_data = (
                    self.service.users()
                    .messages()
                    .get(userId="me", id=msg["id"], format="full")
                    .execute()
                )

                # Message object fields:
                # https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages#Message

                payload = msg_data.get("payload", {})
                body = self.extract_body(payload)

                headers = {
                    item["name"]: item["value"] for item in payload.get("headers", {})
                }

                msg_entry = {
                    "id": msg["id"],
                    "headers": {
                        "date": headers.get("Date"),
                        "to": headers.get("To"),
                        "from": headers.get("From"),
                        "subject": headers.get("Subject"),
                    },
                    "body": body,
                }

                messages.append(msg_entry)

            logger.info(f"Obtained {len(messages)} messages matching query: {query}")
            return messages

        except HttpError as error:
            logger.error(
                f"An error occurred while trying to get Gmail messages: {error}"
            )
            raise

    def extract_body(self, payload):
        body_raw = payload.get("body", {}).get("data")

        if body_raw:
            body_html = self.decode64(body_raw)
            body = self.get_text(body_html)
        else:
            parts = payload.get("parts", [])
            body = []
            for idx, p in enumerate(parts):
                body_raw = p["body"]["data"]
                body_decoded = self.decode64(body_raw)
                body_text = self.get_text(body_decoded)
                body_text_stripped = (
                    body_text.replace("\r", "").replace("\t", "").replace("\n", "")
                )
                body.append({f"part{idx}": body_text_stripped})
        return body

    def get_text(self, html):
        return BeautifulSoup(html, "html.parser").get_text()

    def decode64(self, body_raw):
        return base64.urlsafe_b64decode(body_raw + "==").decode("utf-8")
