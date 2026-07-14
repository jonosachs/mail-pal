from config import load_secrets
from services.slack.msg_builder import (
    build_static_blocks,
    build_review_blocks,
)

import requests
from requests import HTTPError

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

import logging

logger = logging.getLogger(__name__)


class SlackClient:
    def __init__(self, client=None, channel=None):
        self.client = client or self.build_client()
        self.channel = channel or "C0AMF67KHM4"

    def build_client(self):
        secrets = load_secrets()
        client = WebClient(token=secrets.slack_bot_user_token)
        return client

    def send_new_msg(self, msg_blocks: list):
        try:
            response = self.client.chat_postMessage(
                channel=self.channel, text="New Message", blocks=msg_blocks
            )
            return response
        except SlackApiError as e:
            logger.error(
                "⚠️ Error sending Slack message: %s. Provided schema: %s",
                e,
                msg_blocks,
            )
            raise

    # By default, a message published via response_url will be sent as an ephemeral message:
    # https://docs.slack.dev/interactivity/handling-user-interaction/#acknowledgment_response
    def send_response(self, response_url, slack_payload: dict):
        try:
            response = requests.post(url=response_url, json=slack_payload, timeout=5)
            response.raise_for_status()
            logger.info("✅ Response sent to Slack")
            return response
        except HTTPError:
            logger.exception("⚠️ Error sending response to Slack")
            raise

    def send_events_for_approval(self, events: list):
        logger.info("📡 Sending events for approval via Slack")
        num_sent = 0
        for e in events:
            msg_blocks = build_review_blocks(e)
            response = self.send_new_msg(msg_blocks)
            if response["ok"]:
                num_sent += 1
            else:
                logger.error(
                    f"⚠️ Failed to extract an event: {response.get('error', '')}"
                )

        logger.info(f"✅ Sent {num_sent} Slack messages.")

    def send_abort_msg(self, msg):
        slack_msg = build_static_blocks(msg)
        self.send_new_msg(slack_msg)
