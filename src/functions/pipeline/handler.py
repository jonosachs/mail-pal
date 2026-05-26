from services.google.gmail import Gmail
from services.google.gemini import Gemini
from services.google.gcal import Calendar
from services.slack.client import SlackClient
from services.aws.db import DeclinedEvents
from services.http_responses import ok, error

import logging

logger = logging.getLogger(__name__)

gmail = Gmail()
llm = Gemini()
cal = Calendar()
db = DeclinedEvents()
slack = SlackClient()


def lambda_handler(_event, _context):
    """
    RunPipelineFunction
    """

    try:
        emails = gmail.get_mail()

        if not emails:
            slack.send_abort_msg("🛑 No new emails.")
            return ok("🛑 No new emails")

        # Get existing and recently declined events to avoid re-creating
        existing_events = cal.get_existing_events()
        declined_events = db.get_all()

        payload = llm.extract_events(emails, existing_events, declined_events)

        if not payload.events:
            reasons = payload.notes
            slack.send_abort_msg(f"🛑 No new events: {reasons}")
            return ok("🛑 No new events")

        slack.send_events_for_approval(payload.events)

        return ok("✅ Pipeline complete")

    except Exception as e:
        msg = f"⚠️ Pipeline failed: {e}"
        logger.exception(msg)
        slack.send_abort_msg(msg)
        return error("⚠️ Pipeline failed")
