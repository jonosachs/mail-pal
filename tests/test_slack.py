import pytest
from services.slack import build_msg, send_msg

def test_send_msg():
  mock_event = {
    Event(
      id_='18e4f2a1b3c9d001' 
      title='Team Standup' 
      from_='Jane Smith' 
      date='2026-03-25' 
      time='09:00' 
      duration_minutes=60 
      start='2026-03-25T09:00:00+11:00' 
      end='2026-03-25T10:00:00+11:00' 
      location='https://zoom.us/j/123456789' 
      description='Please come prepared to discuss your priorities.' 
      confidence=1.0
    )
  }
  
  msg_schema = build_msg(event=mock_event)
  send_msg(msg_schema)