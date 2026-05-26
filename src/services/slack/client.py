from config import load_secrets
from src.services.slack.msg_builder import (
    build_static_msg,
    build_declined_msg,
    build_review_msg,
)

import requests
from requests import HTTPError

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from enum import Enum
import logging

logger = logging.getLogger(__name__)
secrets = load_secrets()


class SlackClient:
    def __init__(self, client=None, channel=None):
        self.client = client or WebClient(token=secrets["SLACK_BOT_USER_TOKEN"])
        self.channel = channel or "C0AMF67KHM4"

    def send_new_msg(self, slack_schema: list):
        try:
            response = self.client.chat_postMessage(
                channel=self.channel, text="fallback", blocks=slack_schema
            )
            return response
        except SlackApiError as e:
            logger.error(
                "⚠️ Error sending Slack message: %s. Provided schema: %s",
                e,
                slack_schema,
            )
            raise

    def send_ack(self, response_url):
        """
        Send Slack progress update message (Slack requires responses within 3 seconds).
        Uses reply url instead of timestamp
        Replaces original Slack msg.
        """

        payload = {
            "replace_original": True,
            "text": "Processing..",
        }

        try:
            response = requests.post(url=response_url, json=payload, timeout=5)
            logger.info("✅ Successfully sent ack msg to Slack")
            return response
        except HTTPError:
            logger.exception("⚠️ Error sending ack message to Slack")
            raise

    def update_msg_by_ts(self, ts: str, slack_schema: list):
        """Replace previous msg. Requires timestamp"""
        try:
            response = self.client.chat_update(
                channel=self.channel, ts=ts, blocks=slack_schema, text="fallback"
            )
            return response
        except SlackApiError as e:
            logger.error(
                "⚠️ Error updating Slack message: %s. Provided blocks: %s",
                e,
                slack_schema,
            )
            raise

    def send_events_for_approval(self, events: list):
        logger.info("📡 Sending events for approval via Slack")
        sent = 0
        for e in events:
            slack_msg = build_review_msg(e)
            response = self.send_new_msg(slack_msg)
            if response["ok"]:
                sent += 1
            else:
                logger.error(f"⚠️ Failed to extract an event: {response['error']}")

        logger.info(f"✅ Sent {sent} Slack messages.")

    def send_abort_msg(self, msg):
        slack_msg = build_static_msg(msg)
        self.send_new_msg(slack_msg)
