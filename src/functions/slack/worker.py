from models.slack_action_payload import SlackActionPayload
from services.slack.event_review import handle_user_action
from services.http_responses import ok, error
import logging

logger = logging.getLogger(__name__)


def worker_handler(event, context):
    payload = SlackActionPayload.model_validate(event)

    # Handle approve/decline instruction from user
    try:
        handle_user_action(payload)
        return ok("✅ Slack worker pipeline complete")

    except Exception:
        logger.exception("⚠️ Error handling Slack event")
        return error("⚠️ Internal Server Error")
