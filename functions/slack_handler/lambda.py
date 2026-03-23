import json
from urllib.parse import parse_qs, unquote_plus
import logging
from services.gcal import Calendar
from models.event import Event
import os 
import hmac, hashlib
import time
from config import load_secrets

# Initialize the logger
logger = logging.getLogger()
logger.setLevel("INFO")
  
def lambda_handler(event, context):
  try:
    # Verifying requests from Slack 
    # https://docs.slack.dev/authentication/verifying-requests-from-slack/
    
    # Grab your Slack Signing Secret
    slack_signing_secret = load_secrets()['SLACK_SIGNING_SECRET']
    # Use the raw request body, without headers, before it has been deserialized from JSON
    raw_body = event["body"]
    # Extract the timestamp header from the request.
    timestamp = event["headers"]["X-Slack-Request-Timestamp"]
    
    if abs(time.time() - int(timestamp)) > 60 * 60 * 12:
      # Ignore if timestamp is more than 12 hours from local time.
      return
    
    # Concatenate the version number, the timestamp, and the request body together
    sig_basestring = 'v0:' + timestamp + ':' + raw_body
    
    # Hash the resulting string, using the signing secret as a key, and taking the hex digest of the hash.
    my_signature = 'v0=' + hmac.new(
      slack_signing_secret, 
      sig_basestring
    ).hexdigest()
    
    # Compare the resulting signature to the header on the request.
    slack_signature = event["headers"]["X-Slack-Signature"]
    
    if hmac.compare_digest(my_signature, slack_signature):
      # hooray, the request came from Slack!
      
      decoded = unquote_plus(raw_body)  # decodes URL-encoded characters
      body = parse_qs(decoded) # dict of key→list pairs
      slack_payload = json.loads(body["payload"][0])
      action = slack_payload["actions"][0]                                                                  
      action_id = action["action_id"]
      value = action["value"] 
      
      if action_id == "approve":
        
        event_object = Event.model_validate_json(value)
        gcal = Calendar()
        gcal.create_event(event_object)

        return {
            "statusCode": 200,
            "body": "Calender event created successfully"
        }
      else:
        return {
            "statusCode": 200,
            "body": "Calender event denied"
        }
    else:
      return {
        "statusCode": 401,
          "body": "Authentication failed"
      }
  except Exception as e:
      logger.error(f"Error: {str(e)}")
      raise