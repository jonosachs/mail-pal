from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from config import load_secrets


def get_credentials():
    secrets = load_secrets()

    credentials = Credentials(
        token=None,
        refresh_token=secrets["GOOGLE_REFRESH_TOKEN"],
        client_id=secrets["GOOGLE_CLIENT_ID"],
        client_secret=secrets["GOOGLE_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
    )

    credentials.refresh(Request())
    return credentials
