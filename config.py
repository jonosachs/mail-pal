from dotenv import load_dotenv
from botocore.exceptions import ClientError, NoCredentialsError
import os
import boto3
import json
import logging

load_dotenv(override=True)

logger = logging.getLogger(__name__)

KEYS = [
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "GOOGLE_REFRESH_TOKEN",
    "MAILBOXES",
    "GEMINI_API_KEY",
    "EMAILS",
    "SLACK_SIGNING_SECRET",
    "SLACK_WEBHOOK_URL",
    "SLACK_BOT_USER_TOKEN"
]

# Only runs once when the module is first imported
_secrets = None


def load_secrets():
    """Try obtain secrets from cache else get from AWS or locally if not running in Lambda"""

    global _secrets

    if not _secrets:
        # AWS_LAMBDA_FUNCTION_NAME is set by AWS on Lambda functions at runtime
        isLambda = os.getenv("AWS_LAMBDA_FUNCTION_NAME")

        if isLambda:
            _secrets = get_secrets_fromAWS()
        else:
            _secrets = get_secrets_locally()

    for key, value in _secrets.items():
        if not value:
            logger.error(f"{key}: {'MISSING'}")

    return _secrets


def get_secrets_locally():
    secrets = {}
    for key in KEYS:
        secrets[key] = os.getenv(key)
    return secrets


def get_secrets_fromAWS():
    """Get secrets from AWS Secret Manager"""

    secret_name = os.getenv("AWS_SECRETS_MAN")
    region_name = os.getenv("AWS_REGION")

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)

        secrets_AWS = json.loads(get_secret_value_response["SecretString"])

        secrets_local = {}
        for key in KEYS:
            secrets_local[key] = secrets_AWS[key]

        return secrets_local

    # For a list of exceptions thrown, see
    # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html#API_GetSecretValue_Errors
    except NoCredentialsError:
        logger.error("AWS credentials not found")
        raise
    except ClientError as e:
        logger.error(f"Error occured while trying to get secrets from AWS: {e}")
        raise
