from google import genai
from models.event import Events
from services.llm.llm_base import LlmBase
from services.llm.prompt import build_prompt
from config import load_secrets
from google.genai import errors, types
import logging
import time
import httpx

logger = logging.getLogger(__name__)
RETRYABLE_CODES = {408, 429, 500, 502, 503, 504}


class Gemini(LlmBase):
    def __init__(self, client=None):
        if client:
            self.client = client
        else:
            self.secrets = load_secrets()
            self.client = client or genai.Client(
                api_key=self.secrets.gemini_api_key,
                http_options=types.HttpOptions(timeout=90_000),
            )

    def extract_events(self, emails, existing_events, seen_events) -> Events | None:
        logger.info("📡 Contacting Gemini API..")

        prompt_contents = f"""
        {build_prompt()}
        Existing Events:
        {existing_events}
        Recently Seen Events:
        {seen_events}
        Emails:
        {emails}
        """

        max_attempts = 3
        for attempt in range(max_attempts):
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

                # Events object includes Gemini notes (useful to explain why events were dropped)
                return events_obj

            except (httpx.TimeoutException, errors.APIError) as e:
                if isinstance(e, errors.APIError) and e.code not in RETRYABLE_CODES:
                    logger.exception("⚠️ Non-retryable Gemini API error")
                    raise

                if attempt == max_attempts - 1:
                    logger.exception("⚠️ Gemini failed after exhausting retries")
                    raise

                # attempt 1: 90 + 30 = 120sec
                # attempt 2: ..120, + 90 + 60 = 270sec
                # attempt 3: ..270, + 90 = 360sec
                # AWS timeout set to 420sec to allow for runtime
                logger.exception("Gemini error, retrying")
                time.sleep(30 * (attempt + 1))
