from services.aws.db import DeclinedEvents
from services.slack.client import SlackClient
from services.slack.msg_builder import (
    build_delete_original_payload,
    build_static_blocks,
    build_declined_blocks,
)
from services.google.gcal import Calendar

from enum import Enum
import logging

logger = logging.getLogger(__name__)

db = DeclinedEvents()
slack = SlackClient()
gcal = Calendar()


class Action(str, Enum):
    APPROVE = "approve"
    DECLINE = "decline"
    UNDO = "undo"


def handle_user_action(payload):
    if payload.action == Action.APPROVE:
        approve_event(payload)
    elif payload.action == Action.DECLINE:
        decline_event(payload)
    elif payload.action == Action.UNDO:
        undo_declined_event(payload)
    else:
        raise ValueError(f"Unknown action: {payload.action}")


def approve_event(payload):
    # Create calendar event
    gcal.create_event(payload.event)

    blocks = build_static_blocks(f"✅ Event approved: {payload.event_preview}")
    slack_payload = build_delete_original_payload("Event approved", blocks)

    slack.send_response(payload.response_url, slack_payload)


def decline_event(payload):
    # Send Slack confirmation msg (includes undo button)
    blocks = build_declined_blocks(
        f"❌ Event declined: {payload.event_preview}", payload.event
    )
    slack_payload = build_delete_original_payload("Event declined", blocks)
    slack.send_response(payload.response_url, slack_payload)


def undo_declined_event(payload):
    approve_event(payload)
