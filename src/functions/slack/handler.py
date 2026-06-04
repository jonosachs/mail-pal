from services.slack.parser import parse_slack_event
from services.slack.validator import validate
from services.http_responses import unauthorised, ok
import boto3
import logging
import os

logger = logging.getLogger(__name__)

lambda_client = boto3.client("lambda")


def lambda_handler(event, context):
    """
    SlackHandlerFunction
    Parse Slack response payload (event) and send ack (HTTP 200 OK)
    """

    # Validate request was from Slack
    result = validate(event)
    if not result.is_valid:
        return unauthorised(f"Authentication failed: {result.reason}")

    # Parse Slack event as SlackActionPayload object
    payload = parse_slack_event(event)

    # Call asynchronous Lambda to do heavy work outside routine
    # Allows return of 200 OK within Slack required 3-sec timeframe
    worker_function_name = os.environ["SLACK_WORKER_FUNCTION_NAME"]
    lambda_client.invoke(
        FunctionName=worker_function_name,
        InvocationType="Event",
        Payload=payload.model_dump_json().encode("utf-8"),
    )

    logger.info("✅ Sent HTTP 200 OK to Slack")
    return ok("ok")
