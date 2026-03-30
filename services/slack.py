from config import load_secrets
from models.event import Event
from requests import HTTPError, Response, RequestException
import requests
import logging

secrets = load_secrets()
logger = logging.getLogger(__name__)


def post(url: str, payload: dict) -> Response:
    """
    Slack Post request handler. Uses json= parameter.
    Note: Slack webhook just returns HTTP 200 'ok' on success.
    """
    try:
        response = requests.post(url=url, json=payload, timeout=5)
        response.raise_for_status()
        logger.info("Successfully sent msg to Slack")
        return response
    except HTTPError as e:
        raise HTTPError(f"Error sending msg to Slack: {e}") from e


def send_slack_webhook(payload: dict) -> Response:
    """
    Sends Slack message (using incoming webhook) to get user decision.
    Requies activating incoming webhooks on Slack management dashboard.
    """

    webhook_url = secrets["SLACK_WEBHOOK_URL"]
    response = post(webhook_url, payload)
    return response


def build_slack_msg(event: Event) -> dict:
    """
    Builds structured Slack actions message.
    """

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


def confirm_user_action(slack_response_url: str, event: Event, approved: bool):
    """
    Send Slack msg confirming user decision (approve/decline).
    Replaces original message.
    """

    payload = (
        {
            "replace_original": True,
            "text": (
                f"✓ Event created: {event.title} {event.date}"
                if approved
                else f"✗ Event declined: {event.title} {event.date}"
            ),
        },
    )
    post(slack_response_url, payload)


def send_update_msg(response_url: str, msg: str):
    """
    Send Slack progress update message (Slack requires responses within 3 seconds).
    Replaces original Slack msg.
    """

    payload = {
        "replace_original": True,
        "text": msg,
    }
    response = post(response_url, payload)
    return response


def delete_msg():
    # TODO: Implement delete Slack msg method
    pass
