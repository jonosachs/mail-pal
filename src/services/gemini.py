from google import genai
from models.event import Events
from services.llm_base import LlmBase
from services.prompt import prompt
from config import load_secrets
from google.genai import errors
import logging

logger = logging.getLogger(__name__)


class Gemini(LlmBase):
    def __init__(self, client=None):
        self.secrets = load_secrets()
        self.client = client or genai.Client(api_key=self.secrets["GEMINI_API_KEY"])

    def extract_events(self, exist_events, declined_events, emails) -> Events:
        logger.info("📡 Contacting Gemini API..")

        prompt_contents = f"""
        {prompt}
        Existing Events:
        {exist_events}
        Recently Declined Events:
        {declined_events}
        Emails:
        {emails}
        """

        try:
            logger.info("⌛️ Attempting to extract events..")
            response = self.client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt_contents,
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": Events.model_json_schema(),
                },
            )

            # Validate LLM response matches Events shape
            events_obj = Events.model_validate_json(response.text)
            events = events_obj.events  # Events.events -> List[Event]

            if events:
                logger.info(
                    f"✅ Extracted {len(events)} events from {len(emails)} emails."
                )
            else:
                logger.info(f"❌ No valid events found in {len(emails)} emails.")

            # Events object includes gemini notes (useful to explain why events were dropped)
            return events_obj

        except errors.APIError:
            logger.exception("⚠️ An error occured while trying to extract events")
            raise
