import requests
from config import load_secrets
from models.event import Event
import logging

secrets = load_secrets()

logger = logging.getLogger(__name__)
logger.setLevel("INFO")

def send_msg(msg):
  webhook_url = secrets['SLACK_WEBHOOK_URL']
  try:
    response = requests.post(webhook_url, json=msg)
    return response
  except requests.exceptions.RequestException as e:
    print(f"An error occured while trying to send a Slack msg: {e}")
    raise

def build_msg(event: Event) -> dict:
  return {
      "blocks": [
          {
              "type": "section",
              "text": {
                  "type": "mrkdwn",
                  "text": f"*{event.title}*\n{event.from_} | {event.date} {event.time} | {event.duration_minutes} mins\n{event.description}"
              }
          },
          {
              "type": "actions",
              "elements": [
                  {
                      "type": "button",
                      "text": {"type": "plain_text", "text": "Approve"},
                      "style": "primary",
                      "action_id": "approve",
                      "value": event.model_dump_json()
                  },
                  {
                      "type": "button",
                      "text": {"type": "plain_text", "text": "Deny"},
                      "style": "danger",
                      "action_id": "deny",
                      "value": event.id_
                  }
              ]
          }
      ]
  }

def send_confirmation(response_url: str, event: Event, approved: bool):
  logger.info("Sending decision acknowledgement msg to Slack..")
  try:
    response = requests.post(response_url, json={
      "replace_original": True,
      "text": f"✓ Event created: {event.title}" if approved else f"✗ Event declined: {event.title}"
    })
    logger.info(f"{response.status_code}, {response.text}, User response recieved")
  except requests.exceptions.RequestException as e:
    logger.error(f"An error occured while trying to send decision acknowledgement msg to Slack: {e}")
      
    
  
    