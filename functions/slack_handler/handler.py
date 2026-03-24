import json
from urllib.parse import parse_qs, unquote_plus
import logging
from services.gcal import Calendar
from services.slack import send_confirmation
from models.event import Event
import hmac, hashlib
import time
from config import load_secrets

# Initialize the logger
logger = logging.getLogger(__name__)
logger.setLevel("INFO")

def lambda_handler(event, context):
  try:
    # Verifying requests from Slack 
    # https://docs.slack.dev/authentication/verifying-requests-from-slack/
    
    # Grab your Slack Signing Secret
    secrets = load_secrets()
    slack_signing_secret = secrets['SLACK_SIGNING_SECRET']
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
      slack_signing_secret.encode(), 
      sig_basestring.encode(),
      hashlib.sha256
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
      event_object = Event.model_validate_json(value)
      response_url = slack_payload["response_url"]
      
      if action_id == "approve":
        gcal = Calendar()
        gcal.create_event(event_object)

        send_confirmation(response_url=response_url, event=event_object, approved=True)
        
        return {
            "statusCode": 200,
            "body": "Calender event created successfully"
        }
      else:
        send_confirmation(response_url=response_url, event=event_object, approved=False)
       
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
    
    

    