import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import load_secrets
from models.event import Event

logger = logging.getLogger(__name__)

secrets = load_secrets()

_slack_token = secrets["SLACK_BOT_USER_TOKEN"]
_client = WebClient(token=_slack_token)


def get_blocks(text: str) -> list:
    return [{"type": "section", "text": {"type": "mrkdwn", "text": text}}]


def send_msg(msg_blocks: list | None = None, text: str | None = None):
    """Send new message not associated with previous"""

    if not msg_blocks and not text:
        raise KeyError("Missing param")
    if text:
        msg_blocks = get_blocks(text)
    try:
        response = _client.chat_postMessage(
            channel="C0AMF67KHM4", text="fallback", blocks=msg_blocks
        )
        return response
    except SlackApiError as e:
        logger.error(e)
        raise


def update_msg(ts: str, msg_blocks: list | None = None, text: str | None = None):
    """Replace previous msg. Requires timestamp"""

    if not msg_blocks and not text:
        raise KeyError("Missing param")
    if text:
        msg_blocks = get_blocks(text)

    try:
        response = _client.chat_update(
            channel="C0AMF67KHM4", ts=ts, blocks=msg_blocks, text="fallback"
        )
        return response
    except SlackApiError as e:
        logger.error(e)
        raise


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
                    "text": {"type": "plain_text", "text": "Deny"},
                    "style": "danger",
                    "action_id": "deny",
                    "value": event.model_dump_json(),
                },
            ],
        },
    ]
