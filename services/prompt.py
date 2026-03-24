from datetime import datetime

local_dt = datetime.now().astimezone()

prompt = f"""
  Today is {local_dt.strftime('%Y-%m-%d')}.
  Local Timezone is {local_dt.tzinfo}
  
  Your job is to filter the provided emails and find any important events, or actions items, and return calendar entries for each.

  Only include events that are important or actually require a response.
  Return a JSON array per the schema provided. 
  Only include events with confidence > 0.7.
  Do not include events for dates that are in the past.
  Return empty array [] if no events found.
  Return JSON only, no other text.
"""
