from abc import ABC, abstractmethod
from typing import List, Optional
from .entity import Item, ItemCategory

class ItemRepository(ABC):
    @abstractmethod
    def save(self, item: Item) -> Item:
        pass

    @abstractmethod
    def get_by_id(self, item_id: str) -> Optional[Item]:
        pass

    @abstractmethod
    def get_by_owner_id(self, owner_id: str) -> List[Item]:
        pass
    
    @abstractmethod
    def search(self, keyword: Optional[str], category: Optional[ItemCategory]) -> List[Item]:
        pass