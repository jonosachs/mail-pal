from src.services.aws.db import DeclinedEvents
from src.services.slack.client import SlackClient
from src.services.slack.msg_builder import build_static_msg, build_declined_msg
from src.services.google.gcal import Calendar

from enum import Enum
import logging

logger = logging.getLogger(__name__)

db = DeclinedEvents()
slack = SlackClient()
gcal = Calendar()


class Action(str, Enum):
    APPROVE = "approve"
    DECLINE = "decline"


def handle_user_action(payload):
    if payload.action == Action.APPROVE:
        approve_event(payload)
    else:
        decline_event(payload)


def approve_event(payload):
    # Create calendar event
    gcal.create_event(payload.event)

    # Send Slack confirmation msg
    slack_msg = build_static_msg(f"✅ Event approved: {payload.event_preview}")
    slack.update_msg_by_ts(payload.ts, slack_msg)


def decline_event(payload):
    # Write declined event to db
    event_id = db.add(payload.event)

    # Send Slack confirmation msg
    slack_msg = build_declined_msg(
        f"❌ Event declined: {payload.event_preview}", event_id
    )
    slack.update_msg_by_ts(payload.ts, slack_msg)
