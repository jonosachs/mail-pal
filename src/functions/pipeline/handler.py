from services.google.gmail import Gmail
from services.llm.gemini import Gemini
from services.google.gcal import Calendar
from services.slack.client import SlackClient
from services.aws.db import EventsStore
from services.http_responses import ok, error

import logging

logger = logging.getLogger(__name__)

gmail = Gmail()
llm = Gemini()
cal = Calendar()
db = EventsStore()
slack = SlackClient()


def lambda_handler(_event, _context):
    """
    RunPipelineFunction
    """

    try:
        # Get recent emails to search for possible events
        emails = gmail.get_mail()

        if not emails:
            slack.send_abort_msg("🛑 No new emails.")
            return ok("🛑 No new emails")

        # Get existing and recently seen events to avoid re-creating
        existing_events = cal.get_existing_events()
        seen_events = db.get_all()

        # Extract event candidates from emails using LLM
        payload = llm.extract_events(emails, existing_events, seen_events)

        if payload is None:
            raise ValueError("LLM returned no payload")

        if not payload.events:
            reasons = payload.notes
            slack.send_abort_msg(f"🛑 No new events: {reasons}")
            return ok("🛑 No new events")

        # Write proposed events to db
        # This loop required before sending to Slack as it sets the source_url
        for event in payload.events:
            # Build the source email url from the event id
            source_url = f"https://mail.google.com/mail/u/0/#inbox/{event.id_}"
            event.source_url = source_url
            # Write to db and pass the returned UUID id to the event object
            event_id = db.add(event)
            event.db_id = event_id

            print(f"✅ Event {event_id} written to db")

        # Send proposed events to Slack for user approval
        slack.send_events_for_approval(payload.events)

        return ok("✅ Pipeline complete")

    except Exception as e:
        msg = f"⚠️ Pipeline failed: {e}"
        logger.exception(msg)
        slack.send_abort_msg(msg)
        return error("⚠️ Pipeline failed")
