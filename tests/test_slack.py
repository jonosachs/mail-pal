import pytest
from services.slack import build_slack_msg, send_slack_webhook
from tests.mock_event import mock_event

# Run single test: python -m pytest tests/test_slack.py -s

def test_send_msg():
    msg_schema = build_slack_msg(event=mock_event)
    response = send_slack_webhook(msg_schema)

    assert response.status_code == 200



