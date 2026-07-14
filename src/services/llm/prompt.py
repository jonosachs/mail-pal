from datetime import datetime
from zoneinfo import ZoneInfo
from config import load_secrets


def build_prompt() -> str:
    secrets = load_secrets()

    local_dt = datetime.now(ZoneInfo("Australia/Melbourne")).isoformat()

    prompt = f"""
    Today is {local_dt}.
      
    Your job is to review the provided emails and find any important events, or actions items, and return calendar entries for each.

    You will also be provided with a list of already seen events. Do not re-create these. 
    A known 'gotcha' is recreating events that are just reminders about already seen events. Avoid this.

    Rules:
    Only include events that are important or actually require a response.
    Return a JSON array per the schema provided. 
    Only include events with confidence > 0.7.
    Do not include events for dates that are in the past.
    Return empty array [] if no events found.
    Return JSON only, no other text.

    When deciding which events to extract, the following user-specified filters should also be considered:
    {secrets.user_specific_prompt}
    """

    return prompt
