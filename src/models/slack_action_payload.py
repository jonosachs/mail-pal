from pydantic import BaseModel
from models.event import Event
from services.slack.event_review import Action


class SlackActionPayload(BaseModel):
    ts: str | None
    response_url: str | None
    channel_id: str | None
    user_id: str | None
    event: Event
    event_preview: str
    action: Action
