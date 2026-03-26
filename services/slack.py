import requests
from config import load_secrets
from models.event import Event
import logging

secrets = load_secrets()

logger = logging.getLogger(__name__)


def send_msg(msg):
    webhook_url = secrets["SLACK_WEBHOOK_URL"]
    try:
        response = requests.post(webhook_url, json=msg)
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occured while trying to send a Slack msg: {e}")
        raise


def build_msg(event: Event) -> dict:
    return {
        "blocks": [
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
    }


def send_confirmation(response_url: str, event: Event, approved: bool):
    try:
        response = requests.post(
            response_url,
            json={
                "replace_original": True,
                "text": (
                    f"✓ Event created: {event.title} {event.date}"
                    if approved
                    else f"✗ Event declined: {event.title} {event.date}"
                ),
            },
        )
        if response.status_code != 200:
            logger.error(f"Something went wrong: {response}")
            return
        logger.info("Sent decision acknowledgement msg to Slack.")
    except requests.exceptions.RequestException as e:
        logger.error(
            f"An error occured while trying to send decision acknowledgement msg to Slack: {e}"
        )
        raise


def send_processing(response_url: str):
    try:
        response = requests.post(
            response_url,
            json={"replace_original": True, "text": "Processing request.."},
        )
        if response.status_code != 200:
            logger.error(f"Something went wrong: {response}")
            return
        logger.info("Sent processing msg to Slack.")
    except requests.exceptions.RequestException as e:
        logger.error(
            f"An error occured while trying to send a 'processing' msg to Slack: {e}"
        )


def delete_msg():
    return
