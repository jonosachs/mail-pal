from urllib.parse import parse_qs
from services.gcal import Calendar, build_schema
from models.event import Event
from config import load_secrets
from services.slack_client import SlackClient
import hmac
import hashlib
import json
import logging
import time

logger = logging.getLogger(__name__)
sc = SlackClient()


def ok(msg: str = ""):
    return {"statusCode": 200, "body": msg}


def lambda_handler(event, context):
    """
    SlackHandlerFunction
    Processes Slack response payload (event)
    """

    # Validate request was from Slack
    if not request_validated(event):
        return {"statusCode": 401, "body": "Authentication failed"}

    ts = None
    try:
        # Send ack message to Slacks (required within 3 secs)
        # Requires unpacking event to get the respones url.
        payload = unpack_payload(event)
        response_url = payload["response_url"]
        sc.ack(response_url)

        # Handle approve/decline instruction from user
        handle_user_response(payload=payload)
        ts = payload["message"]["ts"]

    except Exception as e:
        logger.exception("⚠️ Error handling Slack event")
        # TODO: may fail before ts is defined
        if ts:
            sc.update_msg(ts=ts, text=f"⚠️ SlackHandlerFunction: {e}.")
        raise


def handle_user_response(payload: dict):
    ts = payload["message"]["ts"]
    actions = payload["actions"][0]
    action_id = actions["action_id"]
    value = actions["value"]
    event_obj = Event.model_validate_json(value)  # Returns validated Pydantic model.

    logger.info(f"ℹ️ Recieved user response: {action_id}")

    if action_id == "approve":
        gcal = Calendar()
        gcal.create_event(event_obj)
        sc.update_msg(
            ts=ts, text=f"✅ event created: {event_obj.title} {event_obj.date}"
        )
        success_msg = "✅ Calender event created successfully"
        logger.info(success_msg)
        return ok(success_msg)
    else:
        declined_msg = "❌ Calendar event declined"
        sc.update_msg(
            ts=ts, text=f"❌ Event declined: {event_obj.title} {event_obj.date}"
        )
        logger.info(declined_msg)
        return ok(declined_msg)


def unpack_payload(event) -> dict:
    raw_body = event["body"]

    decoded = parse_qs(raw_body)
    payload_str = decoded["payload"][0]  # unwraps the list
    return json.loads(payload_str)


def request_validated(event) -> bool:
    """
    Verify requests from Slack
        Template: https://docs.slack.dev/authentication/verifying-requests-from-slack/
    """

    # Grab your Slack Signing Secret
    secrets = load_secrets()
    slack_signing_secret = secrets["SLACK_SIGNING_SECRET"]
    # Use the raw request body, without headers, before it has been deserialized from JSON
    raw_body = event["body"]
    # Extract the timestamp header from the request.
    timestamp = event["headers"]["X-Slack-Request-Timestamp"]

    if abs(time.time() - int(timestamp)) > 60 * 60 * 12:
        # Ignore if timestamp is more than 12 hours from local time.
        return False

    # Concatenate the version number, the timestamp, and the request body together
    sig_basestring = "v0:" + timestamp + ":" + raw_body

    # Hash the resulting string, using the signing secret as a key, and taking the hex digest of the hash.
    my_signature = (
        "v0="
        + hmac.new(
            slack_signing_secret.encode(), sig_basestring.encode(), hashlib.sha256
        ).hexdigest()
    )

    # Compare the resulting signature to the header on the request.
    slack_signature = event["headers"]["X-Slack-Signature"]
    return hmac.compare_digest(my_signature, slack_signature)
