from dotenv import load_dotenv
import os

load_dotenv(override=True)

def load_secrets():
  '''Get secrets from AWS Secret Manager'''
  # Load locally for now TODO: load secrets from AWS
  secrets = {
    'GOOGLE_CLIENT_ID':     os.getenv('GOOGLE_CLIENT_ID'),
    'GOOGLE_CLIENT_SECRET': os.getenv('GOOGLE_CLIENT_SECRET'),
    'GOOGLE_API_KEY':       os.getenv('GOOGLE_API_KEY'),
    'GOOGLE_REFRESH_TOKEN': os.getenv('GOOGLE_REFRESH_TOKEN'),
    'MAILBOXES':            os.getenv('MAILBOXES'),
    'GEMINI_API_KEY':       os.getenv('GEMINI_API_KEY')
  }
  
  for key, value in secrets.items():
    if not value:
      print(f"{key}: {'MISSING'}")
  
  return secrets