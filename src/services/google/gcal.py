from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from services.google.credentials import get_credentials
from config import load_secrets
from models.event import Event
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)
load_dotenv(override=True)


class Calendar:
    def __init__(self, service=None):
        if service:
            self.service = service
        else:
            self.creds = get_credentials()
            self.service = build("calendar", "v3", credentials=self.creds)

    def create_event(self, event_obj: Event, attendees: list | None = None) -> str:
        if attendees is None:
            secrets = load_secrets()
            attendees = secrets["EVENT_ATTENDEES_EMAILS"].split(",")

        e = build_event_schema(event_obj, attendees)

        logger.info("📡 Creating event")

        try:
            # sendUpdates param controls who recieves email calendar invites (as opposed
            # to direct event creation).
            event = (
                self.service.events()
                .insert(calendarId="primary", body=e, sendUpdates="externalOnly")
                .execute()
            )

            event_id = event["id"]
            logger.info(f"✅ Created event: {event_id}")

            # TODO: return value not used
            return event_id

        except HttpError:
            logger.exception("⚠️ Error creating event")
            raise

    def get_event(self, event_id) -> dict | None:
        try:
            # Call the Calendar API
            logger.info("📡 Getting event..")
            event = (
                self.service.events()
                .get(calendarId="primary", eventId=event_id)
                .execute()
            )

            if not event:
                logger.info(f"❌ Event {event_id} not found.")
                return

            logger.info(f"✅ Retrieved event: {event_id}")
            return event

        except HttpError:
            logger.exception("⚠️ Error getting event", extra={"event": event_id})

    def get_existing_events(self, query=None, max_results=None) -> list[dict] | None:
        # query param (q) accepts free text search terms
        # Existing bot created events are prepended with [bot]
        query = query or "[bot]"
        max_results = max_results or 10

        try:
            # Call the Calendar API
            logger.info("📡 Getting events..")
            payload = (
                self.service.events()
                .list(
                    calendarId="primary",
                    timeMin=datetime.now(ZoneInfo("Australia/Melbourne")).isoformat(),
                    q=query,
                    maxResults=max_results,
                )
                .execute()
            )

            events = payload.get("items", [])

            if not events:
                logger.info(f"❌ No events found matching query: {query}.")
                return

            logger.info(f"✅ Retrieved {len(events)} events matching query: {query}.")
            return events

        except HttpError:
            logger.exception("⚠️ Error getting existing events")
            return

    # TODO: Unused method
    def delete_event(self, event_id) -> None:
        try:
            response = (
                self.service.events()
                .delete(calendarId="primary", eventId=event_id)
                .execute()
            )

            logger.info(f"✅ Successfully deleted event {event_id}")
            return response

        except Exception:
            logger.exception("⚠️ Error deleting event")


def build_event_schema(e: Event, attendees: list | None = None) -> dict:
    # Google Calendar event schema
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
        "attendees": attendees,
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

    return event
