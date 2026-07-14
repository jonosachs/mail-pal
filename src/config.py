from dotenv import load_dotenv
import os
import boto3
import json
from pydantic import BaseModel
from functools import cache


class Secrets(BaseModel):
    google_client_id: str
    google_client_secret: str
    google_refresh_token: str
    gemini_api_key: str
    extract_events_from_emails: str
    event_attendees_emails: str
    slack_signing_secret: str
    slack_webhook_url: str
    slack_bot_user_token: str
    user_specific_prompt: str


@cache
def load_secrets() -> Secrets:
    """Try obtain secrets from cache else get from AWS or locally if not running in Lambda"""

    # presence of Lambda function indicates AWS environment
    is_remote = os.getenv("AWS_LAMBDA_FUNCTION_NAME")
    secrets = _from_aws() if is_remote else _from_local()
    # Stored keys are upper case. Need lower to match Secrets model
    return Secrets.model_validate({k.lower(): v for k, v in secrets.items()})


def _from_local():
    load_dotenv(override=True)
    return dict(os.environ)


def _from_aws():
    """Get secrets from AWS Secret Manager"""

    region_name = os.getenv("AWS_REGION")
    secret_id = os.getenv("AWS_SECRETS_MAN")

    # Create a Secrets Manager client
    client = boto3.client("secretsmanager", region_name=region_name)
    response = client.get_secret_value(SecretId=secret_id)

    return json.loads(response["SecretString"])
