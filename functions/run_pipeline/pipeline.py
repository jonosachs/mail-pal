from services.gmail import Gmail
from services.gemini import Gemini
from services.gcal import Calendar
from services.slack_client import build_slack_msg, SlackClient
from services.db import Declined
import logging

logger = logging.getLogger(__name__)

gmail = Gmail()
llm = Gemini()
cal = Calendar()
db = Declined()
sc = SlackClient()


def lambda_handler(_event, _context):
    """
    RunPipelineFunction
    """

    try:
        # Accesptable formats for email filter: newer_than:2d, after:2004/04/16
        email_filter = "newer_than:2d"

        # Get emails using Gmail api.
        # Omitting the filter argument will get emails from all time
        emails = gmail.get_mail(filter=email_filter, max_results=20)

        if not emails:
            abort_msg = "❌ RunPipelineFunction: No emails found, aborting pipeline"
            logger.info(abort_msg)
            sc.send_msg(text=abort_msg)
            return

        # Get existing and recently declined events to avoid re-creating
        exist_events = cal.get_exist_events(query="[bot]", max_results=10)
        decl_events = db.get_all()

        # Extract events from emails using Gemini api
        llm_response = llm.extract_events(
            exist_events=exist_events, declined_events=decl_events, emails=emails
        )

        if not llm_response.events:
            abort_msg = f"❌ RunPipelineFunction: No new events, aborting pipeline. LLM notes: {llm_response.notes}"
            logger.info(abort_msg)
            sc.send_msg(text=abort_msg)
            return

        # Build event approval messages and send to Slack
        logger.info("📡 Sending Slack messages")
        sent = 0

        for e in llm_response.events:
            slack_msg = build_slack_msg(e)
            response = sc.send_msg(slack_msg)
            if response["ok"]:
                sent += 1
            else:
                logger.error(f"⚠️ Failed to extract an event: {response['error']}")

        logger.info(f"✅ Sent {sent} Slack messages.")
        return {"statusCode": 200, "body": "✅ Pipeline complete"}

    except Exception as e:
        error = f"⚠️ Pipeline failed: {e}"
        logger.error(error)
        sc.send_msg(text=error)
        return {"statusCode": 500, "body": "⚠️ Pipeline failed"}
