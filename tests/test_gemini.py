from services.gemini import Gemini
from tests.mock_email import mock_email, mock_followup


def test_extract_events():
    gem = Gemini()
    event = gem.extract_events(
        exist_events=None, declined_events=None, emails=mock_email
    )  # -> List[Event]

    assert "team standup" in event[0].title.lower()
    assert "26" in event[0].start


def test_no_recreate_event():
    gem = Gemini()
    event = gem.extract_events(
        exist_events=mock_email, declined_events=None, emails=mock_followup
    )  # -> List[Event]
    assert not event
