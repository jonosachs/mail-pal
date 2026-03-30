from urllib.parse import parse_qs
from services.gcal import Calendar
from services.slack import confirm_user_action, send_update_msg
from models.event import Event
from config import load_secrets
import hmac, hashlib
import json
import logging
import time

# Initialize the logger
logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    """
    Lamba handler for SlackHandlerFunction
    """

    logger.info(f"raw event: {event}")

    # Send immediate processing msg to acknowledge user button click
    # This requires unpacking event to get the respones url.
    raw_body = event["body"]
    logger.info(f"raw event body: {raw_body}")

    decoded = parse_qs(raw_body)
    logger.info(f"decoded event body: {decoded}")

    payload_str = decoded["payload"][0]  # unwraps the list
    payload_json = json.loads(payload_str)

    # Slack payload fields:
    # https://docs.slack.dev/reference/interaction-payloads/block_actions-payload/
    response_url = payload_json["response_url"]
    send_update_msg(response_url, "Processing request..")

    try:
        if request_validated(event):
            actions = payload_json["actions"][0]
            action_id = actions["action_id"]
            value = actions["value"]
            event_obj = Event.model_validate_json(
                value
            )  # Returns validated Pydantic model.

            logger.info(f"Recieved user response: {action_id}")

            if action_id == "approve":
                gcal = Calendar()
                gcal.create_event(event_obj)
                confirm_user_action(
                    slack_response_url=response_url, event=event_obj, approved=True
                )
                return {
                    "statusCode": 200,
                    "body": "Calender event created successfully",
                }
            else:
                confirm_user_action(
                    slack_response_url=response_url, event=event_obj, approved=False
                )
                return {"statusCode": 200, "body": "Calender event denied"}
        else:
            send_update_msg(response_url, "Authentication failed.")
            return {"statusCode": 401, "body": "Authentication failed"}
    except Exception as e:
        logger.error(f"Error occured while handling Slack response: {str(e)}")
        send_update_msg(response_url, "Failed: {e}.")
        raise


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
