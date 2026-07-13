from abc import ABC, abstractmethod
from models.event import Events


class LlmBase(ABC):
    @abstractmethod
    def extract_events(self, emails, existing_events, seen_events) -> Events | None: ...
