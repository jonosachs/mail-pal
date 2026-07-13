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
    # Setup method chaining to match gmail api
    mock_service = MagicMock()
    messages = mock_service.users.return_value.messages.return_value

    # .list call chain: users->messages->list->execute
    mock_id = "id1234"
    mock_response = {"messages": [{"id": mock_id}]}
    messages.list.return_value.execute.return_value = mock_response

    # .get call chain: users->messages->get->execute
    messages.get.return_value.execute.return_value = mock_gmail_payload

    # Run routine with mock service
    gmail = Gmail(service=mock_service)
    query = "newer_than:2d"
    max_results = 1
    response = gmail.get_mail(query, max_results)[0]

    # Check service was called
    messages.list.assert_called_once_with(userId="me", q=query, maxResults=max_results)
    messages.get.assert_called_once_with(userId="me", id=mock_id, format="full")

    # Check message id was passed to get() method
    message_id = messages.get.call_args.kwargs["id"]
    assert message_id == mock_id

    # Check response from get_mail is gmail Message shape
    assert response["id"] == mock_id
    assert "Team Standup" in response["headers"]["subject"]
