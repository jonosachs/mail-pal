
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import load_secrets
import base64
from bs4 import BeautifulSoup
from services.credentials import get_credentials

class Gmail:
  def __init__(self):
    self.secrets = load_secrets()
    self.creds = get_credentials()
    
  def get_mail(self, max_results: 10):
    mailboxes = self.secrets['MAILBOXES'].split(",")
    query = ' OR '.join([f"in:{m}" for m in mailboxes])
    messages = []
    
    try:
      # Call the Gmail API
      print("Calling Gmail API..")
      service = build("gmail", "v1", credentials=self.creds)
      results = (
        service.users().messages().list(
          userId="me", 
          q=query,
          maxResults=max_results, 
        ).execute()
      )
      msgs_by_id = results.get("messages", [])

      if not msgs_by_id:
        print("No messages found.")
        return []
      
      for msg in msgs_by_id:
        msg_data = (
          service.users().messages().get(
            userId="me", 
            id=msg["id"],
            format="full"
          ).execute()
        )
        
        payload = msg_data.get("payload", {})
        body = self.extract_body(payload)

        headers = {item["name"]: item["value"] for item in payload.get("headers", {})}
        
        msg_entry = {
            "id": msg["id"],
            "headers": {
              "date": headers.get("Date"),
              "to": headers.get("To"),
              "from": headers.get("From"),
              "subject": headers.get("Subject")
            },
            "body": body
          }
        
        messages.append(msg_entry)
        
      return messages
    
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")
  
  def extract_body(self, payload):
    body_raw = payload.get("body", {}).get("data")
    
    if body_raw:
      body_html = self.decode64(body_raw)
      body = self.get_text(body_html)
    else:
      parts = payload.get("parts", [])
      body = []
      for idx, p in enumerate(parts):
        body_raw = p["body"]["data"]
        body_decoded = self.decode64(body_raw)
        body_text = self.get_text(body_decoded)
        body_text_stripped = body_text.replace("\r", "").replace("\t", "").replace("\n", "")
        body.append({f"part{idx}": body_text_stripped})
      return body
    
  def get_text(self, html):
    return BeautifulSoup(html, "html.parser").get_text()
  
  def decode64(self, body_raw):
    return base64.urlsafe_b64decode(body_raw + "==").decode("utf-8")