from google import genai
from google.genai import errors
from services.prompt import prompt
from models.event import Event, Events
from typing import List
from config import load_secrets
import logging

logger = logging.getLogger(__name__)
logger.setLevel("INFO")

class Gemini:
  def __init__(self):
    self.secrets = load_secrets()
    self.client = genai.Client(api_key=self.secrets['GEMINI_API_KEY'])

  def extract_events(self, emails) -> List[Event]:
    logger.info("Contacting Gemini API..")

    try:
      logger.info("Attempting to extract events..")
      response = self.client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=f"{prompt}{emails}",
        config={
            "response_mime_type": "application/json",
            "response_json_schema": Events.model_json_schema()
          }
      )
      events_obj = Events.model_validate_json(response.text)
      events = events_obj.events # Pydantic 'Events' object has field events: List[Event]
      num_events = len(events)
      logger.info(f"Event payload from Gemini: {events[0]}")
      if num_events > 0:
        logger.info(f"Extracted {num_events} events from {len(emails)} emails.")
      else:
        logger.info(f"No events found in {len(emails)} emails.")
      return events
    except errors.APIError as e:
      logger.error(f"An error occured while trying to extract events: {e}")