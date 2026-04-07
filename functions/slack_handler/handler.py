from urllib.parse import parse_qs
from services.gcal import Calendar
from models.event import Event
from config import load_secrets
from services.slack_client import update_msg
import hmac, hashlib
import json
import logging
import time

# Initialize the logger
logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    """
    SlackHandlerFunction
    Processes Slack response payload (event)
    """

    try:
        # Send immediate processing msg to acknowledge user button click
        # This requires unpacking event to get the respones url.
        payload = unpack_payload(event)
        ts = payload["message"]["ts"]
        update_msg(ts=ts, text="Processing request..")

        if request_validated(event):
            return handle_user_response(payload=payload)
        else:
            update_msg(ts=ts, text="SlackHandlerFunction: Authentication failed.")
            return {"statusCode": 401, "body": "Authentication failed"}
    except Exception as e:
        logger.error(f"Error handling Slack event: {str(e)}")
        # TODO: may fail before ts is defined
        update_msg(ts=ts, text=f"SlackHandlerFunction: {e}.")
        raise


def handle_user_response(payload):
    ts = payload["message"]["ts"]
    actions = payload["actions"][0]
    action_id = actions["action_id"]
    value = actions["value"]
    event_obj = Event.model_validate_json(value)  # Returns validated Pydantic model.

    logger.info(f"Recieved user response: {action_id}")

    if action_id == "approve":
        gcal = Calendar()
        gcal.create_event(event_obj)
        update_msg(ts=ts, text=f"✓ event created: {event_obj.title} {event_obj.date}")
        success_msg = "Calender event created successfully"
        logger.info(success_msg)
        return {"statusCode": 200, "body": success_msg}
    else:
        declined_msg = "Calendar event declined"
        update_msg(ts=ts, text=f"✗ Event declined: {event_obj.title} {event_obj.date}")
        logger.info(declined_msg)
        return {"statusCode": 200, "body": declined_msg}


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
