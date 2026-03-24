import pytest
from services.gemini import Gemini

def test_extract_events():
  mock_email = [{
      "id": "18e4f2a1b3c9d001",
      "headers": {
          "date": "Mon, 24 Mar 2026 09:00:00 +1100",
          "to": "john@example.com",
          "from": "Jane Smith <jane.smith@example.com>",
          "subject": "Team Standup - Wednesday 25 March"
      },
      "body": "Hi John, just a reminder about our team standup on Wednesday 25 March at 9am. We will be meeting on Zoom at https://zoom.us/j/123456789. Please come prepared to discuss your priorities. Thanks, Jane"
  }]
  
  gem = Gemini()
  event = gem.extract_events(mock_email) # -> List[Event]
  assert "team standup" in event[0].title.lower()
  assert "25" in event[0].start
  
  
  