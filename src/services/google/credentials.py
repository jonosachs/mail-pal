from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from config import load_secrets


# Credentials used for Google services
def get_credentials():
    secrets = load_secrets()

    credentials = Credentials(
        token=None,
        refresh_token=secrets.google_refresh_token,
        client_id=secrets.google_client_id,
        client_secret=secrets.google_client_secret,
        token_uri="https://oauth2.googleapis.com/token",
    )

    credentials.refresh(Request())
    return credentials
