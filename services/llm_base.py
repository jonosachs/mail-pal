from abc import ABC, abstractmethod
from typing import List
from models.event import Event


class LlmBase(ABC):
    @abstractmethod
    def extract_events(self, exist_events, emails) -> List[Event]: ...
