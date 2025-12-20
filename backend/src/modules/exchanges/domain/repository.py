from abc import ABC, abstractmethod
from typing import List, Optional

from .entity import Exchange, ExchangeStatus


class ExchangeRepository(ABC):
    @abstractmethod
    def save(self, exchange: Exchange) -> Exchange:
        pass

    @abstractmethod
    def get_by_id(self, exchange_id: str) -> Optional[Exchange]:
        pass

    @abstractmethod
    def find_by_user(self, user_id: str, role: str) -> List[Exchange]:
        # role: 'requester' or 'owner'
        pass
