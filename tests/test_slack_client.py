from slack_sdk import WebClient
from services.slack_client import send_msg, build_slack_msg
from tests.mock_event import mock_event
import logging

logging.basicConfig(level=logging.DEBUG)


# Run single test: python -m pytest tests/test_slack_client.py -s
def test_connection():
    client = WebClient()
    api_response = client.api_test()


def test_send_msg():
    e = mock_event
    msg_schema = build_slack_msg(event=e)
    response = send_msg(msg_schema)
    print(response.status_code, response.body)
    assert response.status_code == 200
    assert response.body == "ok"
