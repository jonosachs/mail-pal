from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from models.event import Event
from services.credentials import get_credentials
from config import load_secrets
import logging

logger = logging.getLogger(__name__)

event_id = ""


class Calendar:
    def __init__(self):
        self.creds = get_credentials()
        self.secrets = load_secrets()
        self.service = build("calendar", "v3", credentials=self.creds)

    def create_event(self, e: Event) -> str:
        try:
            # Event resource
            # https://developers.google.com/workspace/calendar/api/v3/reference/events#resource

            event = {
                "summary": f"[bot] {e.title}",
                "location": e.location,
                "description": e.description,
                "start": {
                    "dateTime": e.start,
                    "timeZone": "Australia/Melbourne",
                },
                "end": {
                    "dateTime": e.end,
                    "timeZone": "Australia/Melbourne",
                },
                "attendees": [
                    {"email": self.secrets["EMAILS"].split(",")[0]},
                    # {'email': self.secrets["EMAILS"].split(",")[1]}, #TODO: uncomment second email
                ],
                "reminders": {
                    "useDefault": True,
                    # 'overrides': [
                    #   {'method': 'email', 'minutes': 24 * 60},
                    #   {'method': 'popup', 'minutes': 10},
                    # ],
                },
                "source": {"url": e.source_url},
            }

            # Add recurrence tag only if data provided
            if e.recurrence:
                event["recurrence"] = e.recurrence

            # events().insert fields:
            # https://developers.google.com/workspace/calendar/api/v3/reference/events/insert

            event = (
                self.service.events()
                .insert(calendarId="primary", body=event, sendUpdates="externalOnly")
                .execute()
            )

            event_id = event["id"]
            logger.info(f"Created event: {event_id}")
            return event_id

        except HttpError as error:
            logger.error(f"An error occurred while trying to create an event: {error}")
            raise

    def get_event(self, event_id):
        try:
            # Call the Calendar API
            logger.info("Getting event..")
            event = (
                self.service.events()
                .get(calendarId="primary", eventId=event_id)
                .execute()
            )

            if not event:
                logger.info(f"Event {event_id} not found.")
                return

            logger.info(f"Retrieved event: {event["id"]}")
            return event

        except HttpError as error:
            logger.error(f"An error occurred: {error}")

    # Parameters:
    # https://developers.google.com/workspace/calendar/api/v3/reference/events/list
    def get_exist_events(self, query: str, max_results: int = 10):
        try:
            # Call the Calendar API
            logger.info("Getting events..")
            payload = (
                self.service.events()
                .list(calendarId="primary", q=query, maxResults=max_results)
                .execute()
            )

            events = payload.get("items", [])

            if not events:
                logger.info(f"No events found matching query: {query}.")
                return

            logger.info(f"Retrieved {len(events)} events matching query: {query}.")
            logger.info(f"Example event: {events[0]}")
            return events

        except HttpError as error:
            logger.error(f"An error occurred: {error}")

    def delete_event(self, event_id):
        try:
            response = (
                self.service.events()
                .delete(calendarId="primary", eventId=event_id)
                .execute()
            )

            logger.info(f"Successfully deleted event {event_id}")
            return response

        except Exception as e:
            logger.error(f"An error occured trying to delete event: {e}")
