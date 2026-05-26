from abc import ABC, abstractmethod
from typing import List
from models.event import Event


class LlmBase(ABC):
    @abstractmethod
    def extract_events(
        self, emails, existing_events, declined_events
    ) -> List[Event]: ...
