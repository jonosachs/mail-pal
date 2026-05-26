from services.aws.db import DeclinedEvents
from services.slack.client import SlackClient
from services.slack.msg_builder import build_static_msg, build_declined_msg
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

    # Send Slack confirmation msg
    slack_msg = build_static_msg(f"✅ Event approved: {payload.event_preview}")
    slack.update_msg_by_ts(payload.ts, slack_msg)


def decline_event(payload):
    # Write declined event to db and store id
    db_id = db.add(payload.event)
    payload.event.db_id = db_id

    # Send Slack confirmation msg
    slack_msg = build_declined_msg(
        f"❌ Event declined: {payload.event_preview}", payload.event
    )
    slack.update_msg_by_ts(payload.ts, slack_msg)


def undo_declined_event(payload):
    approve_event(payload)

    # Delete database entry
    db_id = payload.event.db_id
    db.delete(db_id)
    logger.info(f"Event {db_id} deleted from database")
