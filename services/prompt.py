from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

local_dt = datetime.now().astimezone()

prompt = f"""
  Today is {local_dt.strftime('%Y-%m-%d')}.
  Local Timezone is {local_dt.tzinfo}
  
  Your job is to filter the provided emails and find any important events, or actions items, and return calendar entries for each.

  Only include events that are important or actually require a response.
  Return a JSON array per the schema provided. 
  Only include events with confidence > 0.7.
  Return empty array [] if no events found.
  Return JSON only, no other text.
"""

class Event(BaseModel):
  id_: str = Field(description="Gmail email id")
  title: str = Field(description="Brief event title")
  from_: str = Field(description="Sender of the email from which the event is generated (use names over addresses)")
  date: str = Field(description="YYYY-MM-DD format")
  time: str = Field(description="HH:MM 24hr format")
  duration_minutes: int = Field(default=60, description="Default 60 if not specified")
  start: str = Field(description="ISO 8601 format e.g. 2026-03-22T15:00:00+11:00")
  end: str = Field(description="ISO 8601 format e.g. 2026-03-22T19:00:00+11:00")
  recurrence: str = Field(description='Defines recurrence rules, format: RRULE:FREQ=;COUNT=', default="")
  location: Optional[str] = Field(default=None, description="Physical or virtual location")
  description: Optional[str] = Field(default=None, description="Additional context")
  confidence: float = Field(description="0-1 confidence score")

class Events(BaseModel):
  events: List[Event]
