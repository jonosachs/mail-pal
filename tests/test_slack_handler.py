import pytest
from functions.slack.handler import lambda_handler
from services.slack.validator import ValidatorOutcome
from tests.mock_slack_event import mock_slack_event
from copy import deepcopy
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.mark.skip(reason="wip")
def test_slack_handler(monkeypatch):
    # Mock Slack event with 'declined' user action
    me = deepcopy(mock_slack_event)

    # Set current timestamp to avoid expiry trigger during validation
    monkeypatch.setattr(
        "functions.slack.handler.validate",
        lambda event: ValidatorOutcome(True),
    )

    # We expect: Validation -> Ack message -> Ephemeral 'declined' acknowledgment msg
    response = lambda_handler(event=me, context=None)

    logger.info(f"{response['statusCode']} {response['body']}")

    assert response["statusCode"] == 200
