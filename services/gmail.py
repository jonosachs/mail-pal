
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from config import load_secrets

class Gmail():
  def __init__(self):
    self.secrets = load_secrets()
    self.creds = self.get_credentials()
  
  def get_credentials(self):
    credentials = Credentials(
      token=None,
      refresh_token=self.secrets['GOOGLE_REFRESH_TOKEN'],
      client_id=self.secrets['GOOGLE_CLIENT_ID'],
      client_secret=self.secrets['GOOGLE_CLIENT_SECRET'],
      token_uri='https://oauth2.googleapis.com/token'
    )
    
    if not credentials.valid:
      print("No valid credentials found, refreshing..")
      credentials.refresh(Request())
    
    return credentials
    
    
  def get_mail(self):
    mailboxes = self.secrets['MAILBOXES'].split(",")
    query = ' OR '.join([f"in:{m}" for m in mailboxes])
    
    try:
      # Call the Gmail API
      print("Calling Gmail API..")
      service = build("gmail", "v1", credentials=self.creds)
      results = (
        service.users().messages().list(
          userId="me", 
          q=query,
          maxResults=5, 
        ).execute()
      )
      messages = results.get("messages", [])

      if not messages:
        print("No messages found.")
        return

      print("Messages:")
      for message in messages:
        print(f'Message ID: {message["id"]}')
        msg = (
          service.users().messages().get(
            userId="me", 
            id=message["id"]
          ).execute()
        )
        print(f'  Subject: {msg["snippet"]}')

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")
  