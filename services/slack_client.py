import logging
from requests import HTTPError
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import load_secrets
from models.event import Event
import requests

logger = logging.getLogger(__name__)
secrets = load_secrets()


class SlackClient:
    def __init__(self, client=None, channel=None):
        self.client = client or WebClient(token=secrets["SLACK_BOT_USER_TOKEN"])
        self.channel = channel or "C0AMF67KHM4"

    def send_msg(self, msg_blocks: list | None = None, text: str | None = None):
        """Send new message not associated with previous"""

        if not msg_blocks and not text:
            raise KeyError("⚠️ Missing param")
        if text:
            msg_blocks = get_blocks(text)
        try:
            response = self.client.chat_postMessage(
                channel=self.channel, text="fallback", blocks=msg_blocks
            )
            return response
        except SlackApiError as e:
            logger.error(
                "⚠️ Error sending Slack message: %s. Provided blocks: %s", e, msg_blocks
            )
            raise

    def ack(self, response_url):
        """
        Send Slack progress update message (Slack requires responses within 3 seconds).
        Uses reply url instead of timestamp
        Replaces original Slack msg.
        """

        payload = {
            "replace_original": True,
            "text": "Processing..",
        }

        try:
            response = requests.post(url=response_url, json=payload, timeout=5)
            logger.info("✅ Successfully sent ack msg to Slack")
            return response
        except HTTPError:
            logger.exception("⚠️ Error sending ack message to Slack")
            raise

    def update_msg(
        self, ts: str, msg_blocks: list | None = None, text: str | None = None
    ):
        """Replace previous msg. Requires timestamp"""

        if not msg_blocks and not text:
            raise KeyError("⚠️ Missing param")
        if text:
            msg_blocks = get_blocks(text)

        try:
            response = self.client.chat_update(
                channel=self.channel, ts=ts, blocks=msg_blocks, text="fallback"
            )
            return response
        except SlackApiError as e:
            logger.error(
                "⚠️ Error updating Slack message: %s. Provided blocks: %s", e, msg_blocks
            )
            raise


def get_blocks(text: str) -> list:
    return [{"type": "section", "text": {"type": "mrkdwn", "text": text}}]


def build_slack_msg(event: Event) -> list:
    """Builds structured Slack actions message."""

    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{event.title}*\n{event.from_} | {event.date} {event.time} | {event.duration_minutes} mins\n{event.description}\n{event.source_url}",
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Approve"},
                    "style": "primary",
                    "action_id": "approve",
                    "value": event.model_dump_json(),
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Decline"},
                    "style": "danger",
                    "action_id": "deny",
                    "value": event.model_dump_json(),
                },
            ],
        },
    ]
