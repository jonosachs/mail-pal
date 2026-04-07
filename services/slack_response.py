import os
from slack_sdk.signature import SignatureVerifier
from slack_sdk.webhook import WebhookClient
from flask import Flask, request, make_response

signature_verifier = SignatureVerifier(
        signing_secret=os.environ["SLACK_SIGNING_SECRET"]
        )
app = Flask(__name__)

@app.route("/slack/events", methods=["POST"])
def slack_app():
    # Verify incoming requests from Slack
    # https://docs.slack.dev/authentication/verifying-requests-from-slack
    if not signature_verifier.is_valid(
        body=request.get_data(),
        timestamp=request.headers.get("X-Slack-Request-Timestamp"),
        signature=request.headers.get("X-Slack-Signature")):
        return make_response("invalid request", 403)

    # Handle a slash command invocation
    if "command" in request.form \
        and request.form["command"] == "/reply-this":
        response_url = request.form["response_url"]
        text = request.form["text"]
        webhook = WebhookClient(response_url)
        # Send a reply in the channel
        response = webhook.send(text=f"You said '{text}'")
        # Acknowledge this request
        return make_response("", 200)

    return make_response("", 404)
