import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from models.event import Event
from services.credentials import get_credentials
from config import load_secrets

class Calendar:
  def __init__(self):
    self.creds = get_credentials()
    self.secrets = load_secrets()
    return
  
  def create_event(self, e: Event):
    try:
      service = build("calendar", "v3", credentials=self.creds)
      
      event = {
        'summary': e.title,
        'location': e.location,
        'description': e.description,
        'start': {
          'dateTime': e.start,
          'timeZone': 'Australia/Melbourne',
        },
        'end': {
          'dateTime': e.end,
          'timeZone': 'Australia/Melbourne',
        },
        'recurrence': [
          e.recurrence
        ],
        'attendees': [
          {'email': self.secrets["EMAILS"].split(",")[0]},
          # {'email': self.secrets["EMAILS"].split(",")[1]}, #TODO: uncomment second email
        ],
        'reminders': {
          'useDefault': True,
          # 'overrides': [
          #   {'method': 'email', 'minutes': 24 * 60},
          #   {'method': 'popup', 'minutes': 10},
          # ],
        },
      }

      event = service.events().insert(calendarId='primary', body=event).execute()
      print(f'Event created: {event.get('htmlLink')}')
    
    except HttpError as error:
      print(f"An error occurred: {error}")

  
  def get_events(self):
    try:
      service = build("calendar", "v3", credentials=self.creds)

      # Call the Calendar API
      print("Calling Calendar API..")
      now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
      print("Getting the upcoming 10 events")
      events_result = (
          service.events()
          .list(
              calendarId="primary",
              timeMin=now,
              maxResults=10,
              singleEvents=True,
              orderBy="startTime",
          )
          .execute()
      )
      events = events_result.get("items", [])

      if not events:
        print("No upcoming events found.")
        return

      # Prints the start and name of the next 10 events
      for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        print(start, event["summary"])

    except HttpError as error:
      print(f"An error occurred: {error}")