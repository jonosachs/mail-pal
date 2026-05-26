from config import load_secrets
from src.models.slack_action_payload import SlackActionPayload
from src.services.aws.db import DeclinedEvents
from src.models.event import Event
from src.services.slack.client import SlackClient

from urllib.parse import parse_qs
import json
import logging


logger = logging.getLogger(__name__)
secrets = load_secrets()
db = DeclinedEvents()
slack = SlackClient()


# Parse Slack event as dict and return SlackResponse object
def parse_slack_event(slack_event) -> SlackActionPayload:
    raw_body = slack_event["body"]
    decoded = parse_qs(raw_body)
    payload_raw = decoded["payload"][0]  # unwraps the list
    payload = json.loads(payload_raw)

    response_url = payload["response_url"]
    ts = payload["message"]["ts"]
    event_raw = payload["actions"]["value"]
    action_id = payload["actions"][0]["action_id"]

    event = Event.model_validate_json(event_raw)  # Returns validated Pydantic model.
    event_preview = f"{event.title} {event.data}"

    return SlackActionPayload(
        ts=ts,
        response_url=response_url,
        event=event,
        event_preview=event_preview,
        action=action_id,
    )
