from models.event import Event


def build_static_msg(text: str) -> list:
    return [{"type": "section", "text": {"type": "mrkdwn", "text": text}}]


def build_declined_msg(msg: str, event: Event) -> list:
    return [
        {"type": "section", "text": {"type": "mrkdwn", "text": msg}},
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Undo/Approve"},
                    "action_id": "undo",
                    "value": event.model_dump_json(),
                }
            ],
        },
    ]


def build_review_msg(event: Event) -> list:
    """Build structured Slack actions message."""

    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"""
📅 *{event.title}*
{event.from_} | {event.date} {event.time} | {event.duration_minutes} mins
{event.description}
{event.source_url}
                """,
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Approve"},
                    "style": "primary",
                    "action_id": "approve",
                    "value": event.model_dump_json(),
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Decline"},
                    "style": "danger",
                    "action_id": "decline",
                    "value": event.model_dump_json(),
                },
            ],
        },
    ]
