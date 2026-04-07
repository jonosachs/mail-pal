import pytest
from functions.slack_handler.handler import lambda_handler
from tests.mock_slack_event import mock_event
from datetime import datetime
import logging
import json

logging.basicConfig(level=logging.DEBUG)


def test_slack_handler():
    me = mock_event
    ts = str(int(datetime.now().timestamp()))
    print(ts)
    me["headers"]["X-Slack-Request-Timestamp"] = ts
    response = lambda_handler(event=mock_event, context=None)
    rjon = json.dumps(response)
    assert "200" in rjon
