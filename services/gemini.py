from google import genai
from google.genai import errors
from services.prompt import prompt
from models.event import Event, Events
from typing import List
from config import load_secrets

class Gemini:
  def __init__(self):
    self.secrets = load_secrets()

  def extract_events(self, emails) -> List[Event]:
    print("Contacting Gemini API..")
    client = genai.Client(api_key=self.secrets['GEMINI_API_KEY'])
    
    try:
      print("Attempting to extract events..")
      response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=f"{prompt}{emails}",
        config={
            "response_mime_type": "application/json",
            "response_json_schema": Events.model_json_schema()
          }
      )
      events = Events.model_validate_json(response.text)
      print("Done.")
      return events.events # return List[Event] instead of Events
    except errors.APIError as e:
      print(e)
    
    print(response.text)