from services.google.gcal import Calendar
from tests.mock_event import mock_event
from unittest.mock import MagicMock
import logging

logger = logging.getLogger(__name__)

mock_service = MagicMock()
cal = Calendar(service=mock_service)


"""
event = (
    self.service.events()
    .insert(calendarId="primary", body=event, sendUpdates="externalOnly")
    .execute()
)
"""


def test_create_event():
    mock_id = {"id": "event1234"}
    events = mock_service.events.return_value
    events.insert.return_value.execute.return_value = mock_id

    event_id = cal.create_event(mock_event)

    assert "Team Standup" in str(events.insert.call_args.kwargs["body"])

    events.insert.assert_called()
    assert event_id == mock_id["id"]
