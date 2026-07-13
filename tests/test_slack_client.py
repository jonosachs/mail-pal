import pytest
from slack_sdk import WebClient
from services.slack.client import SlackClient
from services.slack.msg_builder import build_review_blocks
from tests.mock_event import mock_event
import logging
import json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Uses actual service. Need to implement with MagicMock
@pytest.mark.integration
def test_connection():
    client = WebClient()
    api_response = client.api_test()

    assert api_response["ok"]


# Creates a mock message in Slack (need to delete manually)
@pytest.mark.integration
def test_send_msg():
    # mock_client = MagicMock()
    sc = SlackClient()
    e = mock_event
    msg_blocks = build_review_blocks(event=e)
    response = sc.send_new_msg(msg_blocks)
    msg_response = json.loads(response["message"]["blocks"][1]["elements"][0]["value"])

    assert response.status_code == 200
    assert response["ok"]
    assert msg_response["title"] == e.title
