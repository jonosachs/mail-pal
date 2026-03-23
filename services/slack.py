import requests
from config import load_secrets
from models.event import Event

class Slack:
  def __init__(self):
    self.secrets = load_secrets()
    
  def send(self, msg):
    print("Attempting to send Slack messages..")
    webhook_url = self.secrets['SLACK_WEBHOOK_URL']
    try:
      response = requests.post(webhook_url, json=msg)
      print(response.status_code, response.text, "Messages sent successfuly")
    except requests.exceptions.RequestException as e:
      print(e)
      

  def build_approval_message(self, event: Event) -> dict:
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
  
  
  
    