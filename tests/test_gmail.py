from unittest.mock import MagicMock
from services.google.gmail import Gmail
from mock_email import mock_gmail_payload
import logging

logger = logging.getLogger(__name__)

"""
msg_format = {
  "id": msg["id"],
  "headers": {
    "date": headers.get("Date"),
    "to": headers.get("To"),
    "from": headers.get("From"),
    "subject": headers.get("Subject")
  },
  "body": body
}
"""

"""
self.service.users()
    .messages()
    .list(
        userId="me",
        q=query,
        maxResults=max_results,
    )
    .execute()
"""

"""
self.service.users()
    .messages()
    .get(userId="me", id=msg_id, format="full")
    .execute()
    )
"""


def test_get_mail():
    # Setup mock service and response
    mock_id = "id1234"
    query = "newer_than:2d"
    mock_service = MagicMock()
    mock_response = {"messages": [{"id": mock_id}]}

    # Setup method chaining to match gmail api
    messages = mock_service.users.return_value.messages.return_value
    list_call = messages.list.return_value
    list_call.execute.return_value = mock_response
    get_call = messages.get.return_value
    get_call.execute.return_value = mock_gmail_payload

    # Run routine with mock service
    gmail = Gmail(service=mock_service)
    response = gmail.get_mail(filter=query, max_results=1)[0]

    # Check service was called
    messages.list.assert_called()

    # Check query was passed to list() method
    search_query = messages.list.call_args.kwargs["q"]
    assert query in search_query

    # Check message id was passed to get() method
    message_id = messages.get.call_args.kwargs["id"]
    assert message_id == mock_id

    # Check response from get_mail is gmail Message shape
    assert response["id"] == mock_id
    assert "Team Standup" in response["headers"]["subject"]
