from src.services.slack.client import SlackClient
from src.services.slack.parser import parse_slack_event
import src.services.slack.validator as validator
from src.services.slack.event_review import handle_user_action
from src.services.http_responses import unauthorised


import logging

logger = logging.getLogger(__name__)
slack = SlackClient()


def lambda_handler(event, context):
    """
    SlackHandlerFunction
    Processes Slack response payload (event)
    """

    # Validate request was from Slack
    if not validator.is_valid(event):
        return unauthorised("Authentication failed")

    try:
        # Send ack message to Slack (required within 3 secs)
        payload = parse_slack_event(event)
        slack.send_ack(payload.response_url)

        # Handle approve/decline instruction from user
        handle_user_action(payload)

    except Exception:
        logger.exception("⚠️ Error handling Slack event")
