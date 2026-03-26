import pytest
from services.gemini import Gemini
import logging

mock_email = [
    {
        "id": "18e4f2a1b3c9d001",
        "headers": {
            "date": "Mon, 24 Jun 2026 09:00:00 +1100",
            "to": "john@example.com",
            "from": "Jane Smith <jane.smith@example.com>",
            "subject": "Team Standup - Wednesday 26 June",
        },
        "body": "Hi John, just a reminder about our team standup on Wednesday 26 June at 9am. We will be meeting on Zoom at https://zoom.us/j/123456789. Please come prepared to discuss your priorities. Thanks, Jane",
    }
]

mock_followup = [
    {
        "id": "19f5z0c1b3d2p005",
        "headers": {
            "date": "Tue, 25 Jun 2026 09:39:00 +1100",
            "to": "john@example.com",
            "from": "Jane Smith <jane.smith@example.com>",
            "subject": "Team Meeting",
        },
        "body": "Hi John, another reminder about our team meeting tomorrow. Don't forget like last time! Thanks, Jane",
    }
]


# Run single test: python -m pytest tests/test_gemini.py -s
def test_extract_events():
    gem = Gemini()
    event = gem.extract_events(exist_events=None, emails=mock_email)  # -> List[Event]

    assert "team standup" in event[0].title.lower()
    assert "26" in event[0].start


def test_no_recreate_event():
    gem = Gemini()
    event = gem.extract_events(
        exist_events=mock_email, emails=mock_followup
    )  # -> List[Event]
    assert not event
