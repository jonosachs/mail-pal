from services.gmail import Gmail
from services.gemini import Gemini
from services.slack import build_msg, send_msg
import logging

logger = logging.getLogger(__name__)
logger.setLevel("INFO")

def lambda_handler(_event, _context):                                                                                     
  try:
    gmail = Gmail()
    gemini = Gemini()

    emails = gmail.get_mail(max_results=5)
    cal_events = gemini.extract_events(emails)
    
    # Build approval msg and send to Slack 
    logger.info("Sending Slack messages")
    sent = 0
    for e in cal_events:
      msg = build_msg(e)
      response = send_msg(msg)
      if response.status_code == 200: sent += 1
      
    logger.info(f"Sent {sent} Slack messages.")
    
    return {"statusCode": 200, "body": "Pipeline complete"}
  except Exception as e:
    logger.error(f"Pipeline failed: {e}")
    return {"statusCode": 500, "body": "Pipeline failed"}