import hmac
import hashlib
import time
from config import load_secrets

secrets = load_secrets()


def is_valid(slack_event) -> bool:
    """
    Verify requests from Slack
        Template: https://docs.slack.dev/authentication/verifying-requests-from-slack/
    """

    # Grab your Slack Signing Secret
    slack_signing_secret = secrets["SLACK_SIGNING_SECRET"]
    # Use the raw request body, without headers, before it has been deserialized from JSON
    raw_body = slack_event["body"]
    # Extract the timestamp header from the request.
    timestamp = slack_event["headers"]["X-Slack-Request-Timestamp"]

    if abs(time.time() - int(timestamp)) > 60 * 60 * 12:
        # Ignore if timestamp is more than 12 hours from local time.
        return False

    # Concatenate the version number, the timestamp, and the request body together
    sig_basestring = "v0:" + timestamp + ":" + raw_body

    # Hash the resulting string, using the signing secret as a key, and taking the hex digest of the hash.
    my_signature = (
        "v0="
        + hmac.new(
            slack_signing_secret.encode(), sig_basestring.encode(), hashlib.sha256
        ).hexdigest()
    )

    # Compare the resulting signature to the header on the request.
    slack_signature = slack_event["headers"]["X-Slack-Signature"]
    return hmac.compare_digest(my_signature, slack_signature)
