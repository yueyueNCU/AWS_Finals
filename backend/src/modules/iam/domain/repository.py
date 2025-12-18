from abc import ABC, abstractmethod
from typing import Optional
from .entity import User  

class UserRepository(ABC):
    """
    這是一個抽象類別 (Abstract Base Class)。
    它只定義了方法名稱，沒有實作內容。
    """

    @abstractmethod
    def save(self, user: User) -> User:
        """儲存或更新使用者"""
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """透過 Email 尋找使用者"""
        pass

    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[User]:
        """透過 ID 尋找使用者"""
        pass