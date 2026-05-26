from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from services.google.credentials import get_credentials
from config import load_secrets
from bs4 import BeautifulSoup
import base64
import logging

logger = logging.getLogger(__name__)


class Gmail:
    def __init__(self, service=None):
        self.secrets = load_secrets()
        self.creds = get_credentials()
        self.service = service or build("gmail", "v1", credentials=self.creds)

    def get_msg_ids(self, query, max_results) -> dict:
        try:
            logger.info("📡 Calling Gmail API..")
            results = (
                self.service.users()
                .messages()
                .list(
                    userId="me",  # Key word 'me' indicates authenticated user
                    q=query,
                    maxResults=max_results,
                )
                .execute()
            )
            return results.get("messages", [])
        except HttpError as error:
            err = f"⚠️ Error getting Gmail msg ids: {error}"
            logger.exception(err)
            raise HttpError(err) from error

    def get_msg(self, msg_id) -> dict:
        try:
            response = (
                self.service.users()
                .messages()
                .get(userId="me", id=msg_id, format="full")
                .execute()
            )
            return response
        except HttpError as error:
            raise HttpError(f"⚠️ Error getting Gmail messages: {error})") from error

    def get_mail(self, filter=None, max_results=None) -> list:
        """Get emails using Gmail API."""

        # Acceptable formats for email filter: newer_than:2d, after:2004/04/16
        filter = filter or "newer_than:2d"
        max_results = max_results or 10

        # Get comma separated mailboxes to include in search
        # Gmail uses OR operator to split search criteria
        mailboxes = self.secrets["MAILBOXES"].split(",")
        query = " OR ".join([f"in:{m}" for m in mailboxes])
        # Add custom filter arguments if provided
        if filter:
            query += f" {filter}"

        # Gmail uses 2-step process for msg retrieval
        # 1- list() returns msg ids matching search query
        msg_ids = self.get_msg_ids(query=query, max_results=max_results)

        if not msg_ids or len(msg_ids) < 1:
            logger.info(f"❌ No msgs found matching query: {query}.")
            return []

        logger.info(f"✅ Found {len(msg_ids)} msg ids matching search query")

        # 2- get() returns an email matching the id
        messages = []
        for msg in msg_ids:
            msg_id = msg["id"]
            gmail_payload = self.get_msg(msg_id)

            if not gmail_payload:
                logger.error(f"⚠️ Could not find msg: {msg_id}")
                continue

            # Parse payload as normalised message schema
            msg_schema = build_msg(msg_id, gmail_payload)
            messages.append(msg_schema)

        if not messages:
            logger.error(f"⚠️ Couldn't get emails from ids: {msg_ids}")
            return []

        logger.info(f"✅ Obtained {len(messages)} messages matching query: {query}")
        return messages


# Helper methods
def extract_body(payload):
    body_raw = payload.get("body", {}).get("data")

    if body_raw:
        body_html = decode64(body_raw)
        body = extract_text(body_html)
    else:
        parts = payload.get("parts", [])
        body = []
        for idx, p in enumerate(parts):
            body_raw = p.get("body", {}).get("data")
            if not body_raw:
                continue
            body_decoded = decode64(body_raw)
            body_text = extract_text(body_decoded)
            body_text_stripped = (
                body_text.replace("\r", "").replace("\t", "").replace("\n", "")
            )
            body.append({f"part{idx}": body_text_stripped})
    return body


def extract_text(html):
    return BeautifulSoup(html, "html.parser").get_text()


def decode64(body_raw):
    return base64.urlsafe_b64decode(body_raw + "==").decode("utf-8")


def build_msg(msg_id, msg_data) -> dict:
    payload = msg_data.get("payload", {})
    body = extract_body(payload)
    headers = {item["name"]: item["value"] for item in payload.get("headers", {})}

    return {
        "id": msg_id,
        "headers": {
            "date": headers.get("Date"),
            "to": headers.get("To"),
            "from": headers.get("From"),
            "subject": headers.get("Subject"),
        },
        "body": body,
    }
