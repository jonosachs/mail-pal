from config import load_secrets
from models.slack_action_payload import SlackActionPayload
from models.event import Event

from urllib.parse import parse_qs
import json
import logging

logger = logging.getLogger(__name__)
secrets = load_secrets()


# Parse Slack event as dict and return SlackResponse object
def parse_slack_event(slack_event) -> SlackActionPayload:
    raw_body = slack_event["body"]
    decoded = parse_qs(raw_body)
    payload_raw = decoded["payload"][0]  # unwraps the list
    payload = json.loads(payload_raw)

    # Obtain response details
    response_url = payload["response_url"]
    ts = payload["message"]["ts"]

    # Obtain event details
    action_id = payload["actions"][0]["action_id"]
    event_raw = payload["actions"]["value"]
    event = Event.model_validate_json(event_raw)  # Returns validated Pydantic model.
    event_preview = f"{event.title} {event.data}"

    return SlackActionPayload(
        ts=ts,
        response_url=response_url,
        event=event,
        event_preview=event_preview,
        action=action_id,
    )
