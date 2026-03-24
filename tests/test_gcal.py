import pytest
from services.gcal import Calendar
from models.event import Event
import datetime

def test_create_event():
  # recurrence field is omitted for single events
  test_event = Event(
    id_="18e4f2a1b3c9d001",
    title="Team Standup",
    from_="Jane Smith",
    date="2026-03-25",
    time="09:00",
    duration_minutes=30,
    start="2026-03-25T09:00:00+11:00",
    end="2026-03-25T09:30:00+11:00",
    location="Zoom: https://zoom.us/j/123456789",
    description="Weekly team standup to discuss priorities and blockers.",
    confidence=0.95
  )

  cal = Calendar()
  event_id = cal.create_event(test_event)
  retrieved_event = cal.get_event(event_id)
  
  # Event fields:
  # https://developers.google.com/workspace/calendar/api/v3/reference/events#resource
  assert retrieved_event["summary"] == test_event.title
  assert retrieved_event["start"]["dateTime"] == test_event.start
  
  response = cal.delete_event(event_id)
  assert response == ""
  

  