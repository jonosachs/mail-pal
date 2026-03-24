from pydantic import BaseModel, Field, ConfigDict, SkipValidation
from typing import List, Optional
import datetime

class Event(BaseModel):
  model_config = ConfigDict(
    arbitrary_types_allowed=True
  )
  id_: str = Field(description="Gmail email id")
  title: str = Field(description="Brief event title")
  from_: str = Field(description="Sender of the email from which the event is generated (use names over addresses)")
  date: str = Field(description="YYYY-MM-DD format")
  time: str = Field(description="HH:MM 24hr format")
  duration_minutes: int = Field(default=60, description="Default 60 if not specified")
  start: str = Field(description="ISO 8601 format string e.g. 2026-03-22T15:00:00+11:00")
  end: str = Field(description="ISO 8601 format string e.g. 2026-03-22T19:00:00+11:00")
  recurrence: Optional[List[str]] = Field(default=None, description='Format: RRULE:FREQ=;COUNT=, omit field for single event')
  location: Optional[str] = Field(default=None, description="Physical or virtual location")
  description: Optional[str] = Field(default=None, description="Additional context, keep it under 500 chars")
  confidence: float = Field(description="0-1 confidence score")
  
class Events(BaseModel):
  events: List[Event]