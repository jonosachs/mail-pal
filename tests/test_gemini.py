import pytest
from services.llm.gemini import Gemini
from tests.mock_email import mock_email, mock_followup


# Calls actual API. Need to implement with MagicMock
@pytest.mark.integration
def test_extract_events():
    gem = Gemini()
    event = gem.extract_events(
        emails=mock_email, existing_events=None, seen_events=None
    )  # -> List[Event]

    assert event is not None
    assert "team standup" in event[0].title.lower()
    assert "26" in event[0].start


# Calls actual API. Need to implement with MagicMock
@pytest.mark.integration
def test_no_recreate_event():
    gem = Gemini()
    event = gem.extract_events(
        emails=mock_followup,
        existing_events=mock_email,
        seen_events=None,
    )  # -> List[Event]

    assert not event
