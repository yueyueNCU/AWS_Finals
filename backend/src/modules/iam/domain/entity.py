from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: str
    email: str
    password_hash: str
    name: str
    is_active: bool = True
    is_admin: bool = False
    avatar_url: Optional[str] = None

    # 你甚至可以在這裡寫純邏輯方法，例如：
    def check_is_admin(self) -> bool:
        return self.is_active and self.is_admin