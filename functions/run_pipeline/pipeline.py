from services.gmail import Gmail
from services.gemini import Gemini
from services.slack import build_msg, send_msg
from services.gcal import Calendar
from datetime import datetime
import logging
import pytz
import os
from dotenv import load_dotenv

load_dotenv(override=True)

logger = logging.getLogger(__name__)


def lambda_handler(_event, _context):
    try:
        gmail = Gmail()
        llm = Gemini()
        cal = Calendar()

        email_filter = os.getenv("EMAIL_FILTER")

        # Get emails using Gmail api
        # Omitting the filter argument will get emails from all time
        emails = gmail.get_mail(filter=email_filter, max_results=5)

        if not emails:
            logger.info("No emails found, ending pipeline")
            return

        # Get existing events to avoid re-creating
        exist_events = cal.get_exist_events(query="[bot]")

        # Extract events from emails using Gemini api
        proposed_events = llm.extract_events(exist_events=exist_events, emails=emails)

        if not proposed_events:
            logger.info("No new events, ending pipeline")
            return

        # Build event approval msg and send to Slack
        logger.info("Sending Slack messages")
        sent = 0
        for e in proposed_events:
            msg = build_msg(e)
            response = send_msg(msg)
            if response.status_code == 200:
                sent += 1
            else:
                logger.error(f"Something went wrong: {response}")

        logger.info(f"Sent {sent} Slack messages.")
        return {"statusCode": 200, "body": "Pipeline complete"}

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        return {"statusCode": 500, "body": "Pipeline failed"}


def today():
    aest = pytz.timezone("Australia/Melbourne")
    return datetime.now(aest).strftime("%Y/%m/%d")
