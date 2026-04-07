from services.gmail import Gmail
from services.gemini import Gemini
from services.gcal import Calendar
from services.slack_client import send_msg, build_slack_msg
import logging

logger = logging.getLogger(__name__)


def lambda_handler(_event, _context):
    """
    RunPipelineFunction
    """

    try:
        gmail = Gmail()
        llm = Gemini()
        cal = Calendar()

        # Accesptable formats for email filter: newer_than:2d, after:2004/04/16
        email_filter = "newer_than:12d"

        # Get emails using Gmail api.
        # Omitting the filter argument will get emails from all time
        emails = gmail.get_mail(filter=email_filter, max_results=20)

        if not emails:
            abort_msg = "RunPipelineFunction: No emails found, aborting pipeline"
            logger.info(abort_msg)
            send_msg(text=abort_msg)
            return

        # Get existing events to avoid re-creating
        exist_events = cal.get_exist_events(query="[bot]", max_results=10)

        # Extract events from emails using Gemini api
        extracted_events = llm.extract_events(exist_events=exist_events, emails=emails)

        if not extracted_events:
            abort_msg = "RunPipelineFunction: No new events, aborting pipeline"
            logger.info(abort_msg)
            send_msg(text=abort_msg)
            return

        # Build event approval messages and send to Slack
        logger.info("Sending Slack messages")
        sent = 0

        for e in extracted_events:
            slack_msg = build_slack_msg(e)
            response = send_msg(slack_msg)
            if response["ok"]:
                sent += 1
            else:
                logger.error(f"Failed to extract an event: {response['error']}")

        logger.info(f"Sent {sent} Slack messages.")
        return {"statusCode": 200, "body": "Pipeline complete"}

    except Exception as e:
        error = f"Pipeline failed: {e}"
        logger.error(error)
        send_msg(text=error)
        return {"statusCode": 500, "body": "Pipeline failed"}
